import re
import sys
import configparser
from evtx import PyEvtxParser
from py2neo import Graph
from lxml import etree
from datetime import datetime
import log_constants as var


def update_record(record_xml):
    rep_xml = record_xml.replace(
        'xmlns="http://schemas.microsoft.com/win/2004/08/events/event"', ""
    )
    fin_xml = rep_xml.encode("utf-8")
    parser = etree.XMLParser(resolve_entities=False)
    return etree.fromstring(fin_xml, parser)


class Event_obj:
    # add new IDs to catch here.
    EVENT_ID_LIST = [
        1102,
        4624,
        4625,
        4662,
        4768,
        4769,
        4776,
        4672,
        4720,
        4726,
        4728,
        4729,
        4732,
        4733,
        4756,
        4757,
        4719,
        5137,
        5141,
    ]

    def __init__(self, record_data):
        self.record_data = record_data
        self.ignore = False
        self.event_id = int(record_data.xpath("/Event/System/EventID")[0].text)
        self.node_tracker = None

        # prepare time
        event_time = record_data.xpath("/Event/System/TimeCreated")[0].get("SystemTime")
        try:
            self.formatted_time = datetime.strptime(
                event_time.split(".")[0], time_string
            )
        except ValueError:
            self.formatted_time = datetime.strptime(
                event_time.split(".")[0], time_string2
            )
        self.event_data = record_data.xpath("/Event/EventData/Data")
        self.logintype = 0
        self.username = "-"
        self.domain = "-"
        self.ipaddress = "-"
        self.hostname = "-"
        self.status = "-"
        self.sid = "-"
        self.authname = "-"
        self.guid = "-"
        self.transfer = None

        # Initial way to minimize bloat in the logs.  This will reduce the amount of irrelevant nodes/edges inside the database.
        if self.event_id in self.EVENT_ID_LIST:
            self.update_event()
        else:
            self.ignore = True

    def __str__(self):
        return str(self.event_id)

    def _event_1102(self):
        namespace = "http://manifests.microsoft.com/win/2004/08/windows/eventlog"
        user_data = self.record_data.xpath(
            "/Event/UserData/ns:LogFileCleared/ns:SubjectUserName",
            namespaces={"ns": namespace},
        )
        domain_data = self.record_data.xpath(
            "/Event/UserData/ns:LogFileCleared/ns:SubjectUserName",
            namespaces={"ns": namespace},
        )
        if user_data[0].text is not None:
            tmp_name = user_data[0].text.split("@")[0]
            if not tmp_name.endswith("$"):
                self.username = f"{tmp_name.lower()}@"
        if domain_data[0].text is not None:
            self.domain = domain_data[0]
        self.node_tracker = "delete log"

    def _event_4662(self):
        for data in self.event_data:
            if (
                data.get("Name") == "SubjectUserName"
                and data.text is not None
                and not re.search(var.UCHECK, data.text)
            ):
                tmp_name = data.text.split("@")[0]
                if not tmp_name.endswith("$"):
                    self.username = f"{tmp_name.lower()}@"

            self.status = "dsync"

    def _event_4672(self):
        for data in self.event_data:
            if (
                data.get("Name") == "SubjectUserName"
                and data.text is not None
                and not re.search(var.UCHECK, data.text)
            ):
                tmp_name = data.text.split("@")[0]
                if not tmp_name.endswith("$"):
                    self.username = f"{tmp_name.lower()}@"
        if self.username != "-":
            self.node_tracker = "admin"

    def _event_4719(self):
        for data in self.event_data:
            if (
                data.get("Name") == "SubjectUserName"
                and data.text is not None
                and not re.search(var.UCHECK, data.text)
            ):
                tmp_name = data.text.split("@")[0]
                if not tmp_name.endswith("$"):
                    self.username = f"{tmp_name.lower()}@"
            if (
                data.get("Name") == "CategoryId"
                and data.text is not None
                and re.search(r"\A%%\d{4}\Z", data.text)
            ):
                category = data.text
            if (
                data.get("Name") == "SubcategoryGuid"
                and data.text is not None
                and re.search(r"\A{[\w\-]*}\Z", data.text)
            ):
                guid = data.text

        self.node_tracker = f"policy {category} {guid}"

    def _event_4720_4726(self):
        for data in self.event_data:
            if (
                data.get("Name") == "TargetUserName"
                and data.text is not None
                and not re.search(var.UCHECK, data.text)
            ):
                tmp_name = data.text.split("@")[0]
                if not tmp_name.endswith("$"):
                    self.username = f"{tmp_name.lower()}@"
        if self.event_id == 4720:
            self.node_tracker = "add user"
        else:
            self.node_tracker = "delete user"

    def _event_4728_4732_4756(self):
        for data in self.event_data:
            if (
                data.get("Name") == "TargetUserName"
                and data.text is not None
                and not re.search(var.UCHECK, data.text)
            ):
                groupname = data.text
            elif (
                data.get("Name") == "MemberSid"
                and data.text not in "-"
                and data.text is not None
                and re.search(r"\AS-[0-9\-]*\Z", data.text)
            ):
                usid = data.text
        self.node_tracker = f"AddGroup {groupname} {usid}"

    def _event_4729_4733_4757(self):
        for data in self.event_data:
            groupname = ""
            usid = ""
            if (
                data.get("Name") == "TargetUserName"
                and data.text is not None
                and not re.search(var.UCHECK, data.text)
            ):
                groupname = data.text
            elif (
                data.get("Name") == "MemberSid"
                and data.text not in "-"
                and data.text is not None
                and re.search(r"\AS-[0-9\-]*\Z", data.text)
            ):
                usid = data.text

            self.node_tracker = f"Remove {groupname} {usid}"

    def _event_5137_5141(self):
        for data in self.event_data:
            if (
                data.get("Name") == "SubjectUserName"
                and data.text is not None
                and not re.search(var.UCHECK, data.text)
            ):
                tmp_name = data.text.split("@")[0]
                if not tmp_name.endswith("$"):
                    self.username = f"{tmp_name.lower()}@"

            self.node_tracker = f"dcshadow {self.formatted_time}"

    def _event_catch_all(self):
        for data in self.event_data:
            # IP
            if (
                data.get("Name") in ["IpAddress", "Wordstation"]
                and data.text is not None
                and self._ip_check(data.text)
            ):
                ipaddress = data.text.split("@")[0]
                ipaddress = ipaddress.lower().replace("::ffff:", "")
                self.ipaddress = ipaddress.replace("\\", "")

            # Host
            if (
                data.get("Name") == "WorkstationName"
                and data.text is not None
                and self._ip_check(data.text)
            ):
                hostname = data.text.split("@")[0]
                hostname = hostname.lower().replace("::ffff:", "")
                self.hostname = hostname.replace("\\", "")

            # Username
            if (
                data.get("Name") == "TargetUserName"
                and data.text is not None
                and not re.search(var.UCHECK, data.text)
            ):
                tmp_name = data.text.split("@")[0]
                if not tmp_name.endswith("$"):
                    self.username = f"{tmp_name.lower()}@"

            # Domain
            if (
                data.get("Name") == "TargetDomainName"
                and data.text is not None
                and not re.search(var.HCHECK, data.text)
            ):
                self.domain = data.text

            # user sid
            if (
                data.get("Name") in ["TargetUserSid", "TargetSid"]
                and data.text is not None
                and re.search(r"\AS-[0-9\-]*\Z", data.text)
            ):
                self.sid = data.text

            # logon type
            if data.get("Name") == "LogonType" and re.search(r"\A\d{1,2}\Z", data.text):
                self.logintype = int(data.text)

            # parse status
            if data.get("Name") == "status" and re.search(r"\A0x\w{8}\Z", data.text):
                self.status = data.text

            # parse Authpkg
            if data.get("Name") == "AuthenticationPackageName" and re.search(
                r"\A\w*\Z", data.text
            ):
                self.authname = data.text

    def _ip_check(self, text_string):

        return (
            not re.search(var.HCHECK, text_string)
            or re.search(var.IPv4_PATTERN, text_string)
            or re.search(var.IPv4_v6_PATTERN, text_string)
            or re.search(var.IPv6_PATTERN, text_string)
        )

    def update_event(self):
        if self.event_id == 1102:
            self._event_1102()
        elif self.event_id == 4662:
            self._event_4662()
        elif self.event_id == 4672:
            self._event_4672()
        elif self.event_id == 4719:
            self._event_4719()
        elif self.event_id in [4720, 4726]:
            self._event_4720_4726()
        elif self.event_id in [4728, 4732, 4756]:
            self._event_4728_4732_4756()
        elif self.event_id in [4729, 4733, 4757]:
            self._event_4729_4733_4757()
        elif self.event_id in [5137, 5141]:
            self._event_5137_5141()
        else:
            self._event_catch_all()


def evtx_file_parse(filename):
    config = configparser.ConfigParser()
    config.read("config.ini")
    try:
        graph_http = (
            "http://"
            + config["DEFAULT"]["NEO4J_USER"]
            + ":"
            + config["DEFAULT"]["NEO4J_PASSWORD"]
            + "@"
            + "neo4j"
            + ":"
            + config["DEFAULT"]["NEO4j_PORT"]
            + "/db/data/"
        )
        GRAPH = Graph(graph_http)
    except:
        sys.exit("[!] Can't connect Neo4j Database.")

    transfer = GRAPH.begin()
    things_to_write = []
    with open(filename, "rb") as evtx_file:
        parser = PyEvtxParser(evtx_file)

        for record in parser.records():

            record_data = update_record(record["data"])
            event = Event_obj(record_data)

            # skip logs that are not in the EVENT_ID_LIST
            if event.ignore:
                continue

            # input()
    transfer.commit()
    # testing123


if __name__ == "__main__":
    # testing
    time_string = "%Y-%m-%dT%H:%M:%S"
    time_string2 = "%Y-%m-%d %H:%M:%S"
    evtx_file_parse("./upload/meow.evtx")
    # evtx_file_parse("upload/ForwardedEvents.evtx")

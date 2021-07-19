import re
from evtx import PyEvtxParser
from py2neo import Graph
from lxml import etree
from datetime import datetime
import log_constants.py as var


def do_stuff(record_xml):
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
        self.ignore = False
        self.event_id = int(record_data.xpath("/Event/System/EventID")[0].text)

        # prepare time
        event_time = record_data.xpath("/Event/System/TimeCreated")[0].get("SystemTime")
        self.formatted_time = datetime.strptime(event_time.split(".")[0], time_string)
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

        # Initial way to minimize bloat in the logs.  This will reduce the amount of irrelevant nodes/edges inside the database.
        if self.event_id in self.EVENT_ID_LIST:
            self.update_event()
        else:
            self.ignore = True

    def __str__(self):
        return str(self.event_id)



    def _event_1102(self):
        pass

    def _event_4662(self):
        pass


    def _event_4719(self):
        pass

    def _event_4720_4726(self):
        pass

    def _event_4728_4732_4756(self):
        pass

    def _event_4729_4733_4757(self):
        pass

    def _event_4762(self):
        for data in self.event_data:
            if (
                data.get("Name") in "SubjectUserName"
                and data.text is not None
                and not re.search(var.UCHECK, data.text)
            ):
                tmp_name = data.text.split("@")[0]
                if not tmp_name.endswith("$"):
                    self.username = f"{tmp_name.lower()}@"

    def _event_5137_5141(self):
        pass

    def _event_catch_all(self):
        for data in self.event_data:
            if (data.get("Name" in ["IpAddress", "Wordstation"])):
                pass

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
    # evtx validation?
    with open(filename, "rb") as evtx_file:
        parser = PyEvtxParser(evtx_file)

        for record in parser.records():

            record_data = do_stuff(record["data"])
            event = Event_obj(record_data)

            # skip logs that are not in the EVENT_ID_LIST
            if event.ignore:
                continue

            # input()


if __name__ == "__main__":
    # testing
    time_string = "%Y-%m-%dT%H:%M:%S"
    evtx_file_parse("./upload/ForwardedEvents.evtx")

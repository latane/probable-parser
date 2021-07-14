from evtx import PyEvtxParser
from py2neo import Graph
from lxml import etree
from datetime import datetime

def do_stuff(record_xml):
    rep_xml = record_xml.replace(
        'xmlns="http://schemas.microsoft.com/win/2004/08/events/event"', ""
    )
    fin_xml = rep_xml.encode("utf-8")
    parser = etree.XMLParser(resolve_entities=False)
    return etree.fromstring(fin_xml, parser)

class Event_obj:
    # add new IDs to catch here.
    EVENT_ID_LIST = [4624, 4625, 4662, 4768, 4769, 4776, 4672, 4720, 4726, 4728, 4729, 4732, 4733, 4756, 4757, 4719, 5137, 5141]
    def __init__(self, record_data):
        self.ignore = False
        self.event_id = int(record_data.xpath("/Event/System/EventID")[0].text)
        #prepare time
        event_time = record_data.xpath("/Event/System/TimeCreated")[0].get("SystemTime")
        self.formatted_time = datetime.strptime(event_time.split('.')[0], time_string)
        self.event_data = record_data.xpath("/Event/EventData/Data")
        
        if self.event_id in self.EVENT_ID_LIST:
            self.update_event()
        else:
            self.ignore = True

    def __str__(self):
        return str(self.event_id)

    def update_event(self):
        if self.event_id == 4672:
            pass
        elif self.event_id in [4728, 4732, 4756]:
            pass
        elif self.event_id in [4729, 4733, 4757]:
            pass
        elif self.event_id == 4662:
            pass
        elif self.event_id in [5137, 5141]:
            pass
        else:
            pass # catch all
            

def evtx_file_parse(filename):
    # evtx validation?
    with open(filename, "rb") as evtx_file:
        parser = PyEvtxParser(evtx_file)

        for record in parser.records():

            record_data = do_stuff(record["data"])
            event = Event_obj(record_data)
            
            if event.ignore:
                continue
            else:
                print(event)
            
            
            # input()


    


if __name__ == "__main__":
    #testing
    time_string = "%Y-%m-%dT%H:%M:%S"
    evtx_file_parse('./upload/ForwardedEvents.evtx')
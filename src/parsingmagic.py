from evtx import PyEvtxParser
from py2neo import Graph
from lxml import etree

def do_stuff(record_xml):
    rep_xml = record_xml.replace(
        'xmlns="http://schemas.microsoft.com/win/2004/08/events/event"', ""
    )
    fin_xml = rep_xml.encode("utf-8")
    parser = etree.XMLParser(resolve_entities=False)
    return etree.fromstring(fin_xml, parser)


def evtx_file_parse(filename):

    # evtx validation?

    with open(filename, "rb") as evtx_file:
        parser = PyEvtxParser(evtx_file)
        # records = list(parser.records())
    
    # for record in records:
        for record in parser.records():
            record_data = do_stuff(record["data"])
            event_id = record_data.xpath("/Event/System/EventID")[0].text
            
            input()


    


if __name__ == "__main__":
    #testing
    evtx_file_parse('./upload/ForwardedEvents.evtx')
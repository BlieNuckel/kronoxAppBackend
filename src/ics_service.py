import json
from typing import List
import urllib3
import urllib3.exceptions as url_except
import datetime as dt  # noqa # pylint: disable=unused-import
from icalendar import Calendar


def main():
    idList: List[str] = []
    with open("json/ids.json") as f:
        idList = json.load(f)

    for id in idList:
        fetchIcsFile(id)


def fetchIcsFile(id):
    kronoxURL = "https://kronox.hkr.se/setup/jsp/Schema.jsp?startDatum=idag&intervallTyp=m&intervallAntal=6&sprak=EN&sokMedAND=true&forklaringar=true&resurser="  # noqa: E501
    schemaURL = "https://schema.hkr.se/setup/jsp/Schema.jsp?startDatum=idag&intervallTyp=m&intervallAntal=6&sprak=EN&sokMedAND=true&forklaringar=true&resurser="  # noqa: E501
    http = urllib3.PoolManager()

    try:
        res = http.request("GET", kronoxURL + id)
        print(res.data)
    except url_except.TimeoutError or url_except.ConnectionError:
        try:
            res = http.request("GET", schemaURL + id)
        except url_except.TimeoutError or url_except.ConnectionError:
            pass

    return res.data


def parse_ics(ics: str) -> List[str]:
    events = []
    ical = Calendar.from_ical(ics)
    for i, component in enumerate(ical.walk()):
        if component.name == "VEVENT":

            event = {}
            event["start"] = {
                "dateTime": component.get("dtstart").dt.isoformat(),
                "timeZone": str(component.get("dtstart").dt.tzinfo),
            }
            event["end"] = {
                "dateTime": component.get("dtend").dt.isoformat(),
                "timeZone": str(component.get("dtend").dt.tzinfo),
            }
            event["title"] = component.get("summary")
            event["location"] = component.get("location")
            event["sequence"] = component.get("sequence")
            try:
                desc = component.get("description").replace("\xa0", " ")
                if "description" in event:
                    event["description"] = desc + "\r\n" + event["description"]
                else:
                    event["description"] = desc

                event["description"] = component.get("description")
            except AttributeError:
                pass

            events.append(event)

    return events

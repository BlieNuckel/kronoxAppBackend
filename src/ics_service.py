from enum import Enum
from typing import Dict, List, Tuple
import urllib3
import urllib3.exceptions as url_except
import datetime as dt  # noqa # pylint: disable=unused-import
from icalendar import Calendar
import re
import dateutil.parser as dateParse

from src.mongoConnector import MongoConnector


def main():
    connection = MongoConnector()
    idList = connection.getCollection("schedule_ids")[0]["schedule_ids"]

    for id in idList:
        cacheIcs(id)


def cacheIcs(id, returnDict: bool = False):
    icsString: str = __fetchIcsFile(id)
    icsList: List[str] = __parseIcs(icsString)
    icsDict: Dict = __listToJson(icsList)
    __saveToCache(id, icsDict)
    if returnDict:
        return icsDict


def __fetchIcsFile(id) -> str:
    kronoxURL = "https://kronox.hkr.se/setup/jsp/SchemaICAL.ics?startDatum=idag&intervallTyp=m&intervallAntal=6&sprak=SV&sokMedAND=true&forklaringar=true&resurser="  # noqa: E501
    schemaURL = "https://schema.hkr.se/setup/jsp/SchemaICAL.ics?startDatum=idag&intervallTyp=m&intervallAntal=6&sprak=SV&sokMedAND=true&forklaringar=true&resurser="  # noqa: E501
    http = urllib3.PoolManager()

    try:
        res = http.request("GET", kronoxURL + id)
    except url_except.TimeoutError or url_except.ConnectionError:
        try:
            res = http.request("GET", schemaURL + id)
        except url_except.TimeoutError or url_except.ConnectionError:
            pass

    return res.data


def __parseIcs(ics: str) -> List[str]:
    events = []
    ical = Calendar.from_ical(ics)
    for i, component in enumerate(ical.walk()):
        if component.name == "VEVENT":
            event = {}
            title, course, lecturer = __titleSplitter(component.get("summary"))

            event["start"] = component.get("dtstart").dt.isoformat()
            event["end"] = component.get("dtend").dt.isoformat()
            event["course"] = course
            event["lecturer"] = lecturer
            event["location"] = str(component.get("location"))
            event["title"] = title

            events.append(event)

    return events


def __titleSplitter(title: str) -> Tuple[str, str, str]:
    PATTERN1 = re.compile("\s+")  # noqa W605
    PATTERN2 = re.compile(",+")

    split_name = re.split("Kurs.grp: | Sign: | Moment: | Program: ", title)
    edit_name = split_name[3]

    edit_name = edit_name.replace(":  :", ":")
    edit_name = edit_name.rstrip(" : ")
    for j in PATTERN1.findall(split_name[3]):
        edit_name = edit_name.replace(j, " ")
    for j in PATTERN2.findall(split_name[3]):
        edit_name = edit_name.replace(j, ",")
    edit_name = edit_name.replace(";", "")

    return (edit_name, split_name[1], split_name[2])


def __listToJson(events: List) -> Dict:
    eventsDict = {}

    for event in events:
        eventDate = dateParse.isoparse(event["start"])

        if str(eventDate.year) not in eventsDict.keys():
            eventsDict[str(eventDate.year)] = {}

        yearDict: Dict = eventsDict[str(eventDate.year)]

        if months(eventDate.month).name not in yearDict.keys():
            yearDict[months(eventDate.month).name] = {}

        monthDict: Dict = yearDict[months(eventDate.month).name]

        if str(eventDate.day) not in monthDict.keys():
            monthDict[str(eventDate.day)] = []

        monthDict[str(eventDate.day)].append(event)

    return eventsDict


def __saveToCache(id: str, data: Dict) -> None:
    data["_id"] = id

    mongoConnection = MongoConnector()
    mongoConnection.addOne("schedules", data)


class months(Enum):
    January = 1
    February = 2
    March = 3
    April = 4
    May = 5
    June = 6
    July = 7
    August = 8
    September = 9
    October = 10
    November = 11
    December = 12


if __name__ == "__main__":
    main()

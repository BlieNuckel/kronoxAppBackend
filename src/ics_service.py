from enum import Enum
import time
from typing import Dict, List, Tuple
import urllib3
import urllib3.exceptions as url_except
import datetime as dt  # noqa # pylint: disable=unused-import
from icalendar import Calendar
import re
import dateutil.parser as dateParser

from src.mongo_connector import MongoConnector
import src.course_color as color


def cacheIcs(id: str, baseUrl: str, returnDict: bool = True):
    icsString: bytes = __fetchIcsFile(id, baseUrl)
    if not isinstance(icsString, bytes):
        raise TypeError
    icsList: List[Dict] = __parseIcs(icsString)
    icsDict: Dict = __listToJson(icsList)
    scheduleObject = __saveToCache(id, icsDict, baseUrl)

    if returnDict:
        return scheduleObject


def __fetchIcsFile(id: str, baseUrl: str) -> str | None:
    schemaURL = f"https://{baseUrl}/setup/jsp/SchemaICAL.ics?startDatum=idag&intervallTyp=m&intervallAntal=6&sprak=SV&sokMedAND=true&forklaringar=true&resurser="  # noqa: E501
    http = urllib3.PoolManager()

    try:
        res = http.request("GET", schemaURL + id)

        if "VEVENT" not in str(res.data):
            raise TypeError
    except url_except.TimeoutError or url_except.ConnectionError or TypeError:
        pass

    return res.data


def __parseIcs(ics: bytes) -> List[Dict]:
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
            event["color"] = color.getColor(course)

            events.append(event)

    return events


def __titleSplitter(title: str) -> Tuple[str, str, str]:

    keyWordContent = {
        "Kurs.grp": "",
        "Sign": "",
        "Moment": "",
        "Program": "",
    }
    splitString = ""
    keywordsInTitle = re.findall(r"(Kurs.grp|Sign|Moment|Program):", title)

    for index, keyword in enumerate(keywordsInTitle):
        if index == 0:
            splitString += f"{keyword}: |"
        elif index == len(keywordsInTitle) - 1:
            splitString += f" {keyword}: "
        else:
            splitString += f" {keyword}: |"

    split_name = re.split(splitString, title)
    try:
        split_name.remove("")
    except ValueError:
        pass

    for index, keyword in enumerate(keywordsInTitle):
        try:
            keyWordContent[keyword] = split_name[index]
        except IndexError:
            print(f"SPLIT NAME: {split_name}")
            print(f"KEYWORD: {keyword}")
            print(f"INDEX: {index}")

    return (
        keyWordContent["Moment"],
        keyWordContent["Kurs.grp"],
        keyWordContent["Sign"],
    )


def __listToJson(events: List[Dict]) -> Dict:
    eventsDict = {}

    for event in events:
        eventDate = dateParser.isoparse(event["start"])

        if str(eventDate.year) not in eventsDict.keys():
            eventsDict[str(eventDate.year)] = {}

        yearDict: Dict[str, Dict[str, List]] = eventsDict[str(eventDate.year)]

        if months(eventDate.month).name.lower() not in yearDict.keys():
            yearDict[months(eventDate.month).name.lower()] = {}

        monthDict: Dict[str, List] = yearDict[
            months(eventDate.month).name.lower()
        ]

        if str(eventDate.day) not in monthDict.keys():
            monthDict[str(eventDate.day)] = [
                {
                    "dayName": days(eventDate.weekday()).name,
                    "date": f"{eventDate.day}/{eventDate.month}",
                }
            ]

        monthDict[str(eventDate.day)].append(event)

    return eventsDict


def __saveToCache(id: str, data: Dict, baseUrl: str) -> None:

    scheduleJson = {}

    scheduleJson["_id"] = id
    scheduleJson["cachedAt"] = time.ctime()
    scheduleJson["baseUrl"] = baseUrl
    scheduleJson["schedule"] = data

    MongoConnector.updateOne("schedules", {"_id": id}, scheduleJson, True)

    return scheduleJson


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


class days(Enum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6

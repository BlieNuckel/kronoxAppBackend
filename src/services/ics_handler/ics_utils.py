import time
from typing import Dict, List, Tuple
import urllib3
import urllib3.exceptions as url_except
import datetime as dt  # noqa # pylint: disable=unused-import
from icalendar import Calendar
import re
import dateutil.parser as dateParser
from src.services.mongo_connector import MongoConnector

import src.util.course_color as color
from src.util.enums import StartDateEnum, days, months


def _fetchIcsFile(id: str, baseUrl: str, startDateTag: StartDateEnum = None, startDate: str = None) -> str | None:
    urlStartDate = ""

    if startDate:
        urlStartDate = startDate
    elif startDateTag:
        urlStartDate = startDateTag.getDateValue()

    schemaURL = f"https://{baseUrl}/setup/jsp/SchemaICAL.ics?startDatum={urlStartDate}&intervallTyp=m&intervallAntal=6&sprak=SV&sokMedAND=true&forklaringar=true&resurser="  # noqa: E501
    http = urllib3.PoolManager()

    try:
        res = http.request("GET", schemaURL + id)

        if "VEVENT" not in str(res.data):
            raise TypeError
    except url_except.TimeoutError or url_except.ConnectionError or TypeError:
        pass

    return res.data


def _parseIcs(ics: bytes) -> List[Dict]:
    events = []
    ical = Calendar.from_ical(ics)
    for i, component in enumerate(ical.walk()):
        if component.name == "VEVENT":
            event = {}
            title, course, lecturer = _titleSplitter(component.get("summary"))

            event["start"] = component.get("dtstart").dt.isoformat()
            event["end"] = component.get("dtend").dt.isoformat()
            event["course"] = course
            event["lecturer"] = lecturer
            event["location"] = str(component.get("location"))
            event["title"] = title
            event["color"] = color.getColor(course)

            events.append(event)

    return events


def _titleSplitter(title: str) -> Tuple[str, str, str]:

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


def _listToJson(events: List[Dict]) -> Dict:
    eventsDict = {}

    for event in events:
        eventDate = dateParser.isoparse(event["start"])

        if str(eventDate.year) not in eventsDict.keys():
            eventsDict[str(eventDate.year)] = {}

        yearDict: Dict[str, Dict[str, List]] = eventsDict[str(eventDate.year)]

        if months(eventDate.month).name.lower() not in yearDict.keys():
            yearDict[months(eventDate.month).name.lower()] = {}

        monthDict: Dict[str, List] = yearDict[months(eventDate.month).name.lower()]

        if str(eventDate.day) not in monthDict.keys():
            monthDict[str(eventDate.day)] = [
                {
                    "dayName": days(eventDate.weekday()).name,
                    "date": f"{eventDate.day}/{eventDate.month}",
                }
            ]

        monthDict[str(eventDate.day)].append(event)

    return eventsDict


def _saveToCache(id: str, data: Dict, baseUrl: str, startDateTag: StartDateEnum) -> Dict:

    scheduleJson = {}
    scheduleJson["_id"] = {"scheduleId": id, "startsAt": startDateTag.value}
    scheduleJson["cachedAt"] = time.ctime()
    scheduleJson["baseUrl"] = baseUrl
    scheduleJson["startsAt"] = startDateTag.value
    scheduleJson["schedule"] = data

    MongoConnector.updateOne(
        "schedules", {"_id": {"scheduleId": id, "startsAt": startDateTag.value}}, scheduleJson, True
    )

    return scheduleJson

import time
import uuid
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

"""Run GET request on specific schedule id and return result string"""
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


def _parseIcs(ics: bytes) -> List[Dict] and List[int]:
    events = []
    ical = Calendar.from_ical(ics)
    uuid_list = []
    for i, component in enumerate(ical.walk()):
        if component.name == "VEVENT":
            event = {}
            temp_uuid = getUniqueScheduleChannelId()
            title, course, lecturer = _titleSplitter(component.get("summary"))

            event["start"] = component.get("dtstart").dt.isoformat()
            event["end"] = component.get("dtend").dt.isoformat()
            event["course"] = course
            event["lecturer"] = lecturer
            event["location"] = str(component.get("location"))
            event["title"] = title
            event["color"] = color.getColor(course)
            event["channel_id"] = temp_uuid
            
            uuid_list.append(temp_uuid)
            events.append(event)
    ## List of dictionaries
    return events, uuid_list


def _parseCompareIcs(ics: bytes, generated_uuids, currentEventsList) -> List[Dict] and List[int]:
    ## Parse list of previous uuids and assign them incrementally
    ## to the events in the new updated schedule, up until they
    ## run out. Then we append new uuids.
    events = []
    ical = Calendar.from_ical(ics)
    flag = False

    ## List of remaining events
    for i, component in enumerate(ical.walk()):
        ## Check if length of new ical does not overflow
        ## current collection of uuids
        if component.name == "VEVENT":
            if i > len(generated_uuids):
                flag = True
                events.append(_createEvent(component, flag, generated_uuids, i))
                continue
            events.append(_createEvent(component, flag, generated_uuids, i))
            if(events[i]['start'] != currentEventsList[i]['start'] | events[i]['end'] != currentEventsList[i]['end']):
                events[i]['channel_id'] = int(str(events[i]['channel_id'])[:-4]+'9999')
                generated_uuids[i] = events[i]['channel_id']
            
    return events, scheduleJson["generated_uuids"]

def _createEvent(component, flag, uuids, i):
    
    ## Utility function for creating an event object
    event = {}
    title, course, lecturer = _titleSplitter(component.get("summary"))
    event["start"] = component.get("dtstart").dt.isoformat()
    event["end"] = component.get("dtend").dt.isoformat()
    event["course"] = course
    event["lecturer"] = lecturer
    event["location"] = str(component.get("location"))
    event["title"] = title
    event["color"] = color.getColor(course)
    event["channel_id"] = getUniqueScheduleChannelId() if flag else uuids[i]
    return event

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

    for i, event in enumerate(events):
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


def _saveToCache(id: str, data: Dict, baseUrl: str, startDateTag: StartDateEnum, uuid_list: List[int]) -> Dict:
    scheduleJson = {}
    scheduleJson["_id"] = {"scheduleId": id, "startsAt": startDateTag.value}
    scheduleJson["cachedAt"] = time.ctime()
    scheduleJson["baseUrl"] = baseUrl
    scheduleJson["startsAt"] = startDateTag.value
    scheduleJson["schedule"] = data
    scheduleJson["generated_uuids"] = uuid_list

    MongoConnector.updateOne(
        "schedules", {"_id": {"scheduleId": id, "startsAt": startDateTag.value}}, scheduleJson, True
    )

    return scheduleJson

def getUniqueScheduleChannelId():
    ## Right shift by 64 bits to avoid 8 byte int limit in MongoDb
    return (uuid.uuid1().int>>64)/2
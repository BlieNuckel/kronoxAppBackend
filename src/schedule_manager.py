from typing import Dict, List
import re
from dateutil import parser as dateParser
import datetime

from src import ics_service
from src.mongo_connector import MongoConnector

PATTERN1 = re.compile("\s+")  # noqa W605
PATTERN2 = re.compile(",+")
PATTERN3 = re.compile(r"(?:(?<=\s)|^)(?:[a-z]|\d+)", re.I)


class ScheduleManager:
    __events: List = []
    __scheduleDict: Dict = {}

    def __init__(self, id: str) -> None:
        self.scheduleDict = self.getIcs(id)

    def getIcs(self, id: str) -> Dict:
        schedulesCollection = MongoConnector.getCollection("schedules")

        for schedule in schedulesCollection:
            if id == schedule["_id"]:
                cacheTime = dateParser.parse(schedule["cachedAt"])
                currentTime = datetime.datetime.now()
                timeDiff = currentTime - cacheTime
                if timeDiff.total_seconds() > 86400:
                    return ics_service.cacheIcs(id, True)
                return schedule

        return ics_service.cacheIcs(id, True)

    def getFilteredSchedule(
        self,
        years: list[str] | None,
        months: list[str] | None,
        days: list[str] | None,
    ) -> Dict:
        filtered: Dict = {}

        yearsList, monthsList, daysList = self.__generateFilterLists(
            years, months, days
        )

        if len(yearsList) < 1:
            if len(monthsList) == 0:
                monthsList = [
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December",
                ]
            for year in self.scheduleDict.keys():
                for month in monthsList:
                    filtered[month.lower()] = {}
                    for day in daysList:
                        try:
                            filtered[month.lower()][
                                day.lower()
                            ] = self.scheduleDict[year.lower()][month.lower()][
                                day.lower()
                            ]
                        except KeyError:
                            pass
        else:
            if len(monthsList) == 0:
                monthsList = [
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December",
                ]
            for year in yearsList:
                filtered[year.lower()] = {}
                if year not in self.scheduleDict.keys():
                    continue
                for month in monthsList:
                    filtered[year.lower()][month.lower()] = {}
                    for day in daysList:
                        try:
                            filtered[year.lower()][month.lower()][
                                day.lower()
                            ] = self.scheduleDict[year.lower()][month.lower()][
                                day.lower()
                            ]
                        except KeyError:
                            pass

        return filtered

    def __generateFilterLists(
        self,
        years: list[str] | None,
        months: list[str] | None,
        days: list[str] | None,
    ) -> tuple[list[str], list[str], list[str]]:
        try:
            if years[0] == "*":
                yearsList = list(self.scheduleDict.keys())
            elif type(years) == list:
                yearsList = years
        except TypeError:
            yearsList = []

        try:
            if months[0] == "*":
                monthsList = [
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December",
                ]
            elif type(months) == list:
                monthsList = months
        except TypeError:
            monthsList = []

        try:
            if days[0] == "*":
                daysList = [str(x) for x in range(1, 32)]
            elif type(days) == list:
                daysList = days
        except TypeError:
            daysList = []

        return yearsList, monthsList, daysList

    @property
    def events(self) -> List:
        return self.__events

    @events.setter
    def events(self, events: List):
        self.__events = events

    @property
    def scheduleDict(self) -> Dict:
        return self.__scheduleDict

    @scheduleDict.setter
    def scheduleDict(self, data: Dict):
        self.__scheduleDict = data

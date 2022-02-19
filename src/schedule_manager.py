from typing import Dict, List
import re

from src import ics_service
from src.mongoConnector import MongoConnector

PATTERN1 = re.compile("\s+")  # noqa W605
PATTERN2 = re.compile(",+")
PATTERN3 = re.compile(r"(?:(?<=\s)|^)(?:[a-z]|\d+)", re.I)


class ScheduleManager:
    __events: List = []
    __scheduleDict: Dict = {}

    def __init__(self, id: str) -> None:
        self.scheduleDict = self.getIcs(id)

    def getIcs(self, id: str) -> Dict:
        mongoConnection = MongoConnector()
        schedulesCollection = mongoConnection.getCollection("schedules")

        for schedule in schedulesCollection:
            if id == schedule["_id"]:
                return schedule

        return ics_service.cacheIcs(id, True)

    def getFilteredSchedule(
        self,
        years: str | list[str] | None,
        months: str | list[str] | None,
        days: str | list[str] | None,
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
            for month in monthsList:
                filtered[month] = {}
                for day in daysList:
                    try:
                        filtered[month][day] = self.scheduleDict[
                            list(self.scheduleDict.keys())[1]
                        ][month][day]
                    except KeyError:
                        pass
                if filtered[month] == {}:
                    filtered.pop(month)
        else:
            for year in yearsList:
                filtered[year] = {}
                if year not in self.scheduleDict.keys():
                    continue
                for month in monthsList:
                    filtered[year][month] = {}
                    for day in daysList:
                        try:
                            filtered[year][month][day] = self.scheduleDict[
                                year
                            ][month][day]
                        except KeyError:
                            pass
                    if filtered[year][month] == {}:
                        filtered[year].pop(month)

        return filtered

        # if years == "*":
        #     yearsList = list(self.scheduleDict.keys())
        # elif type(years) == str:
        #     yearsList = [years]
        # elif type(years) == list:
        #     yearsList = years
        # else:
        #     yearsList = []

        # for year in yearsList:
        #     filtered[year] = {}

        # if months == "*":
        #     if len(filtered.keys()) > 0:
        #         for year in filtered.keys():
        #             monthsList = list(self.scheduleDict[year].keys())
        #             for month in monthsList:
        #                 filtered[year][month] = {}
        #     else:
        #         for year in self.scheduleDict.keys():
        #             monthsList = list(self.scheduleDict[year].keys())
        #             filtered["months"] = []
        #             for month in monthsList:
        #                 filtered["months"].append(dict())
        # elif type(months) == str:
        #     if len(filtered.keys()) > 0:
        #         for year in filtered.keys():
        #             filtered[year][months] = {}
        #     else:
        #         filtered["months"] = []
        #         for year in self.scheduleDict.keys():
        #             filtered["months"].append(dict())
        # elif type(months) == list:
        #     if len(filtered.keys()) > 0:
        #         for year in filtered.keys():

    def __generateFilterLists(
        self,
        years: str | list[str] | None,
        months: str | list[str] | None,
        days: str | list[str] | None,
    ) -> tuple[list, list, list]:
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

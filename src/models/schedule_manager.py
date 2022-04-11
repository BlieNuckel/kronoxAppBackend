from typing import Dict, List

from src.services.ics_handler import ics_service
from src.util.enums import StartDateEnum
from src.services.mongo_connector import MongoConnector


class ScheduleManager:
    __id: str
    __baseUrl: str
    __startDateTag: StartDateEnum | None
    __startDate: str | None
    __scheduleDict: Dict = {}

    def __init__(
        self, id: str, baseUrl: str, startDateTag: StartDateEnum | None = None, startDate: str | None = None
    ) -> None:
        self.__id = id
        self.__baseUrl = baseUrl
        self.__startDateTag = startDateTag
        self.__startDate = startDate

    def fetchIcsWithCaching(self) -> None:
        if not self.__startDateTag:
            raise AttributeError

        try:
            schedulesCollection = MongoConnector.getCollection("schedules")

            for schedule in schedulesCollection:
                if {"scheduleId": self.__id, "startsAt": self.__startDateTag.value} == schedule["_id"]:
                    print("GOT SCHEDULE FROM DB")
                    self.__scheduleDict = schedule
                    self.__scheduleDict["_id"] = self.__scheduleDict["_id"]["scheduleId"]
                    return

            self.__scheduleDict = ics_service.getAndCacheIcs(self.__id, self.__baseUrl, self.__startDateTag)
        except TypeError or TimeoutError as e:
            print(e)
            raise TypeError

    def fetchIcsWithoutCaching(self) -> None:
        if not self.__startDate:
            raise AttributeError

        try:
            self.__scheduleDict = ics_service.getIcs(self.__id, self.__baseUrl, self.__startDate)
        except TypeError or TimeoutError as e:
            print(e)
            raise TypeError

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

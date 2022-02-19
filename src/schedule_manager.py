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

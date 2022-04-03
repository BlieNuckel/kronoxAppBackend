from typing import Dict, List

# from dateutil import parser as dateParser
# import datetime

from src import ics_service


class ScheduleManager:
    __events: List = []
    __scheduleDict: Dict = {}

    def __init__(self, id: str, baseUrl: str, startDate: str) -> None:
        self.scheduleDict = self.getIcs(id, baseUrl, startDate)

    def getIcs(self, id: str, baseUrl: str, startDate: str) -> Dict:
        try:
            return ics_service.cacheIcs(id, baseUrl, startDate)
        except TypeError or TimeoutError:
            return {"error": "Schedule not found at kronox"}

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

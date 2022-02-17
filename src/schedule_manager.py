import json
from typing import Dict, List
import ics_service
import re

PATTERN1 = re.compile("\s+")  # noqa W605
PATTERN2 = re.compile(",+")
PATTERN3 = re.compile(r"(?:(?<=\s)|^)(?:[a-z]|\d+)", re.I)


class ScheduleManager:
    __events: List = []
    __json: Dict = {}

    def __init__(self, id: str) -> None:
        self.json = self.getIcs(id)

    def getIcs(self, id: str) -> str:
        try:
            cachePath = "cache/" + id + ".json"
            with open(cachePath) as icsFile:
                jsonObj = json.load(icsFile)
        except FileNotFoundError:
            ics_service.cacheIcs(id)
            cachePath = "cache/" + id + ".json"
            with open(cachePath) as icsFile:
                jsonObj = json.load(icsFile)

        return jsonObj

    @property
    def events(self) -> List:
        return self.__events

    @events.setter
    def events(self, events: List):
        self.__events = events

    @property
    def json(self) -> Dict:
        return self.__json

    @json.setter
    def json(self, data: Dict):
        self.__json = data

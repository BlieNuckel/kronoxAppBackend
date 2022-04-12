from src.services.ics_handler.ics_service import getAndCacheIcs
from src.services.mongo_connector import MongoConnector
from src.util.enums import StartDateEnum
from typing import Dict
import src.services.ics_handler.ics_utils as ics_utils

def main():
    schedules = MongoConnector.getCollection("schedules")
    for schedule in schedules:
        try:
            middleManParserCache(schedule["_id"]["scheduleId"],
            schedule["generated_uuids"],
            schedule["schedule"],
                schedule["baseUrl"],
                StartDateEnum(schedule["startsAt"]),
                returnDict=False,)
        except TypeError as e:
            print(e)

def middleManParserCache(id: str, schedule, generated_uuids, baseUrl: str, startDateTag: StartDateEnum, returnDict: bool = False) -> Dict | None:
    icsFile: bytes = ics_utils._fetchIcsFile(id, baseUrl, startDateTag=startDateTag)

    currentEventsList = []
    scheduleHolder = [schedule.values() for item in schedule]
    for item in scheduleHolder[0]:
        for i in item:
            for j in item[i]:
                for EVENT in item[i][j]:
                    if list(EVENT.keys())[0] != 'dayName':
                        currentEventsList.append(EVENT)

    if not isinstance(icsFile, bytes):
        raise TypeError
    icsList, new_uuids = ics_utils._parseCompareIcs(icsFile, generated_uuids, currentEventsList)
    icsDict: Dict = ics_utils._listToJson(icsList)
    scheduleObject: Dict = ics_utils._saveToCache(id, icsDict, baseUrl, startDateTag, new_uuids)
    if returnDict:
        return scheduleObject

if __name__ == "__main__":
    main()

from src.services.ics_handler.ics_service import getAndCacheIcs
from src.services.mongo_connector import MongoConnector
from src.util.enums import StartDateEnum
from typing import Dict
import src.services.ics_handler.ics_utils as ics_utils

def main():
    schedules = MongoConnector.getCollection("schedules")
    for schedule in schedules:
        try:
            middleManParserCache(
            schedule["_id"]["scheduleId"],
            schedule,
            schedule["schedule"],
            schedule["baseUrl"],
            StartDateEnum(schedule["startsAt"]),
            returnDict=False,)
        except TypeError as e:
            print(e)

def middleManParserCache(id: str, schedule, generated_uuids, baseUrl: str, startDateTag: StartDateEnum, returnDict: bool = False) -> Dict | None:
    icsFile: bytes = ics_utils._fetchIcsFile(id, baseUrl, startDateTag=startDateTag)
    if not isinstance(icsFile, bytes):
        raise TypeError
    currentEventsList = []
    
    scheduleHolder = (schedule['schedule'])
    for year in scheduleHolder:
        for month in scheduleHolder[year]:
            for day in (scheduleHolder[year][month]):
                for EVENT in scheduleHolder[year][month][day]:
                    if list(EVENT.keys())[0] != 'dayName':
                        currentEventsList.append(EVENT)
    
    
    icsList, new_uuids = ics_utils._parseCompareIcs(icsFile, schedule, currentEventsList)
    icsDict: Dict = ics_utils._listToJson(icsList)
    scheduleObject: Dict = ics_utils._saveToCache(id, icsDict, baseUrl, startDateTag, new_uuids)
    if returnDict:
        return scheduleObject



if __name__ == "__main__":
    main()

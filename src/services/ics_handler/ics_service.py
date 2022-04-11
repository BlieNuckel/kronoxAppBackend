import time
from typing import Dict, List

import src.services.ics_handler.ics_utils as ics_utils
from src.util.enums import StartDateEnum


def getIcs(id: str, baseUrl: str, startDate: str = None) -> Dict:
    icsFile: bytes = ics_utils._fetchIcsFile(id, baseUrl, startDate=startDate)
    if not isinstance(icsFile, bytes):
        raise TypeError
    icsList: List[Dict] = ics_utils._parseIcs(icsFile)
    icsDict: Dict = ics_utils._listToJson(icsList)

    scheduleObject = {}
    scheduleObject["_id"] = id
    scheduleObject["cachedAt"] = time.ctime()
    scheduleObject["baseUrl"] = baseUrl
    scheduleObject["schedule"] = icsDict
    scheduleObject["startsAt"] = startDate

    return scheduleObject


def getAndCacheIcs(id: str, baseUrl: str, startDateTag: StartDateEnum, returnDict: bool = True) -> Dict | None:
    icsFile: bytes = ics_utils._fetchIcsFile(id, baseUrl, startDateTag=startDateTag)
    print("GOT ICS FILE")
    print(icsFile)
    if not isinstance(icsFile, bytes):
        raise TypeError
    icsList: List[Dict] = ics_utils._parseIcs(icsFile)
    print("PARSED ICS FILE")
    icsDict: Dict = ics_utils._listToJson(icsList)
    print("LIST TO JSON")
    scheduleObject: Dict = ics_utils._saveToCache(id, icsDict, baseUrl, startDateTag)
    print("CACHED ICS FILE")
    if returnDict:
        return scheduleObject

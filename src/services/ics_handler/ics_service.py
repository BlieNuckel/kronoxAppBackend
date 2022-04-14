import time
from typing import Dict

import src.services.ics_handler.ics_utils as ics_utils
from src.util.enums import StartDateEnum


def getIcs(id: str, baseUrl: str, startDate: str = None) -> Dict:
    icsFile: bytes = ics_utils._fetchIcsFile(id, baseUrl, startDate=startDate)
    if not isinstance(icsFile, bytes):
        print("ICS FILE NOT BYTES - ics_service.py:11")
        raise TypeError
<<<<<<< Updated upstream
    icsList: List[Dict] = ics_utils._parseIcs(icsFile)
=======

    icsList, uuid_list = ics_utils._parseIcs(icsFile)
>>>>>>> Stashed changes
    icsDict: Dict = ics_utils._listToJson(icsList)

    scheduleObject = {}
    scheduleObject["_id"] = id
    scheduleObject["cachedAt"] = time.ctime()
    scheduleObject["baseUrl"] = baseUrl
    scheduleObject["schedule"] = icsDict
    scheduleObject["startsAt"] = startDate
<<<<<<< Updated upstream
=======
    scheduleObject["generated_uuids"] = uuid_list
>>>>>>> Stashed changes

    return scheduleObject


def getAndCacheIcs(id: str, baseUrl: str, startDateTag: StartDateEnum, returnDict: bool = True) -> Dict | None:
    icsFile: bytes = ics_utils._fetchIcsFile(id, baseUrl, startDateTag=startDateTag)
    if not isinstance(icsFile, bytes):
        print("ICS FILE NOT BYTES - ics_service.py:28")
        raise TypeError
    icsList: List[Dict] = ics_utils._parseIcs(icsFile)
    icsDict: Dict = ics_utils._listToJson(icsList)
    scheduleObject: Dict = ics_utils._saveToCache(id, icsDict, baseUrl, startDateTag)
    if returnDict:
        return scheduleObject

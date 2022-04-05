from src.services.ics_handler.ics_service import getAndCacheIcs
from src.services.mongo_connector import MongoConnector
from src.util.enums import StartDateEnum


def main():
    schedules = MongoConnector.getCollection("schedules")
    for schedule in schedules:
        try:
            getAndCacheIcs(
                schedule["_id"]["scheduleId"],
                schedule["baseUrl"],
                StartDateEnum(schedule["startsAt"]),
                returnDict=False,
            )
        except TypeError as e:
            print(e)


if __name__ == "__main__":
    main()

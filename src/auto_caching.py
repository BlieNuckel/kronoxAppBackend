from src.ics_service import cacheIcs
from src.mongo_connector import MongoConnector


def main():
    schedules = MongoConnector.getCollection("schedules")
    for schedule in schedules:
        cacheIcs(schedule["_id"], schedule["baseUrl"])


if __name__ == "__main__":
    main()

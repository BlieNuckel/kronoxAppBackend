from src.ics_service import cacheIcs
from src.mongo_connector import MongoConnector


def main():
    schedules = MongoConnector.getCollection("schedules")
    for schedule in schedules:
        try:
            cacheIcs(schedule["_id"], schedule["baseUrl"])
        except TypeError as e:
            print(e)


if __name__ == "__main__":
    main()

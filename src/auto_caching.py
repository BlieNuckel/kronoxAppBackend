from datetime import date, timedelta
from src.ics_service import cacheIcs
from src.mongo_connector import MongoConnector


def main():
    schedules = MongoConnector.getCollection("schedules")
    for schedule in schedules:
        try:
            today = date.today()
            startOfWeek = today - timedelta(days=today.weekday())
            cacheIcs(
                schedule["_id"],
                schedule["baseUrl"],
                startOfWeek.strftime("%Y-%m-%d"),
            )
        except TypeError as e:
            print(e)


if __name__ == "__main__":
    main()

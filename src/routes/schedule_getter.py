from fastapi import Response
from datetime import datetime, timedelta

from src.util.schools_info import SCHOOL_BASE_URLS, VALID_SCHOOLS
from src.util.enums import StartDateEnum
from src.models.schedule_manager import ScheduleManager


def getSchedules(
    id: str,
    school: str,
    startTag: str | None,
    year: str | None,
    month: str | None,
    day: str | None,
):
    if school not in VALID_SCHOOLS:
        print("SCHOOL NOT VALID")
        return Response(content="Invalid school query", status_code=404)

    if not startTag and not year and not month and not day:
        print("startTag or date missing")
        return Response(content="You must specify either startDateTag or year, month, and day params", status_code=404)

    """First, attempt to create a StartDateEnum from entered startDate.
    If this fails, fetch the schedule with the given specific date
    WITHOUT caching it."""
    try:
        # ! Ensure backwards compatibility with old app versions!
        """Takes the entered start date and checks it against the
        beginning of the current week. This allows us to use the new
        Enum system, while still supporting the app version that
        uses the endpoint with year, month, and date for accessing
        'start of week' schedules."""
        startDate = ""
        if not startTag and (year and month and day):
            startDate = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        currentTime = datetime.now()
        startOfWeekTimeStamp = currentTime - timedelta(days=currentTime.weekday())

        if startDate == startOfWeekTimeStamp.strftime("%Y-%m-%d"):
            startTag = "startOfWeek"

        # Attempts to create a StartDateEnum from the request
        startDateTag = StartDateEnum(startTag)

        schedule = ScheduleManager(id, SCHOOL_BASE_URLS[school], startDateTag=startDateTag)
        try:
            schedule.fetchIcsWithCaching()
        except TypeError or AttributeError:
            print("ERROR WHILE PARSING/FETCHING")
            return Response(content="An error occured while fetching the schedule", status_code=500)

    except ValueError:
        # Return an error if there is no valid tag AND no valid year, month, and date specified
        if not year or not month or not day:
            print("NO VALID DATE AND ERROR WITH DATETAG")
            return Response(content="Invalid start tag for schedule", status_code=404)

        startDate = f"{year}-{month}-{day}"

        schedule = ScheduleManager(id, SCHOOL_BASE_URLS[school], startDate=startDate)
        try:
            schedule.fetchIcsWithoutCaching()
        except TypeError or AttributeError:
            print("FINAL ERROR")
            return Response(content="An error occured while fetching the schedule", status_code=500)

    return schedule.scheduleDict

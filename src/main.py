from datetime import datetime, timedelta
import re
from typing import Dict
from fastapi import FastAPI, Query, Response

from src.models.schedule_manager import ScheduleManager
from src.kronox_scraper.kronox_scrape import runKronoxSearch
from src.util.enums import StartDateEnum
from src.util.schools_info import SCHOOL_BASE_URLS, VALID_SCHOOLS

app = FastAPI()


@app.get("/testing")
async def root1():
    return "successfully accessed API!"


@app.get("/schedules/{id}")
async def scheduleQuery(
    id: str,
    school: str,
    startTag: str | None = Query(None),
    year: str | None = Query(None),
    month: str | None = Query(None),
    day: str | None = Query(None),
) -> Dict:

    if school not in VALID_SCHOOLS:
        return Response(content="Invalid school query", status_code=404)

    if not startTag and not year and not month and not day:
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

        print(f"Start Date: {startDate}")
        currentTime = datetime.now()
        startOfWeekTimeStamp = currentTime - timedelta(days=currentTime.weekday())

        print(f"Start of Week: {startOfWeekTimeStamp}")

        if startDate == startOfWeekTimeStamp.strftime("%Y-%m-%d"):
            startTag = "startOfWeek"

        # Attempts to create a StartDateEnum from the request
        startDateTag = StartDateEnum(startTag)

        schedule = ScheduleManager(id, SCHOOL_BASE_URLS[school], startDateTag=startDateTag)
        # try:
        schedule.fetchIcsWithCaching()
        # except TypeError or AttributeError:
        #     return Response(content="An error occured while fetching the schedule", status_code=500)

    except ValueError:
        # Return an error if there is no valid tag AND no valid year, month, and date specified
        if not year or not month or not day:
            return Response(content="Invalid start tag for schedule", status_code=404)

        startDate = f"{year}-{month}-{day}"

        schedule = ScheduleManager(id, SCHOOL_BASE_URLS[school], startDate=startDate)
        try:
            schedule.fetchIcsWithoutCaching()
        except TypeError or AttributeError:
            return Response(content="An error occured while fetching the schedule", status_code=500)

    return schedule.scheduleDict


@app.get("/schedules/search/")
async def searchSchedules(school: str, search: str | None = Query(None)):
    if search is None:
        return Response(content="Illegal search query", status_code=404)
    if school not in VALID_SCHOOLS:
        return Response(content="Invalid school query", status_code=404)

    try:
        year = re.search(r"[1-9]\d{3,}", search).group()
        search = search.replace(year, "")
    except AttributeError:
        year = ""
    # filteredResults = await sortValid(fullResults)

    return {"requestedSchedule": runKronoxSearch(search, year, SCHOOL_BASE_URLS[school])}

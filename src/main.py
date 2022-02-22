from typing import Dict
from fastapi import FastAPI, Query, Response

from src.schedule_manager import ScheduleManager
from src.kronox_scraper.kronox_scrape import runKronoxSearch

app = FastAPI()


@app.get("/testing")
async def root1():
    return "successfully accessed API!"


@app.get("/schedule/{id}")
async def scheduleGetter(id: str):
    schedule = ScheduleManager(id)
    return schedule.scheduleDict


@app.get("/schedules/{id}")
async def scheduleQuery(
    id: str,
    year: list[str] | None = Query(None),
    month: list[str] | None = Query(None),
    day: list[str] | None = Query(None),
) -> Dict:
    schedule = ScheduleManager(id)

    if not year and not month and not day:
        return schedule.scheduleDict
    else:
        return schedule.getFilteredSchedule(year, month, day)


@app.get("/schedules/search/")
async def searchSchedules(searchString: str, yearQuery: str = ""):
    if searchString is None:
        return Response(content="Illegal search query", status_code=400)
    return runKronoxSearch(searchString, yearQuery)

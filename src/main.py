import re
from typing import Dict
from fastapi import FastAPI, Query, Response

from src.schedule_manager import ScheduleManager
from src.kronox_scraper.kronox_scrape import runKronoxSearch

app = FastAPI()

VALID_SCHOOLS = ["hkr", "mau", "oru", "ltu"]
SCHOOL_BASE_URLS = {
    "hkr": "schema.hkr.se",
    "mau": "schema.mau.se",
    "oru": "schema.oru.se",
    "ltu": "tenta.ltu.se",
}


@app.get("/testing")
async def root1():
    return "successfully accessed API!"


@app.get("/schedules/{id}")
async def scheduleQuery(
    id: str,
    school: str | None = Query(None),
    year: list[str] | None = Query(None),
    month: list[str] | None = Query(None),
    day: list[str] | None = Query(None),
) -> Dict:
    if school not in VALID_SCHOOLS:
        return Response(content="Invalid school query", status_code=404)

    schedule = ScheduleManager(id, SCHOOL_BASE_URLS[school])

    if "error" in schedule.scheduleDict.keys():
        # return {"schedule": schedule.scheduleDict}
        return Response(content="Schedule not found error", status_code=404)

    if not year and not month and not day:
        return {"schedule": schedule.scheduleDict}
    else:
        return {"schedule": schedule.getFilteredSchedule(year, month, day)}


@app.get("/schedules/search/")
async def searchSchedules(
    school: str | None = Query(None), search: str | None = None
):
    if search is None:
        return Response(content="Illegal search query", status_code=404)
    if school not in VALID_SCHOOLS:
        return Response(content="Invalid school query", status_code=404)

    try:
        year = re.search(r"[1-9]\d{3,}", search).group()
        search = re.sub(r"[1-9]\d{3,}", "", search)
    except AttributeError:
        year = ""
    # filteredResults = await sortValid(fullResults)

    return {
        "requestedSchedule": runKronoxSearch(
            search, year, SCHOOL_BASE_URLS[school]
        )
    }

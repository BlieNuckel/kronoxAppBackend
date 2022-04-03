import re
from typing import Dict
from fastapi import FastAPI, Query, Response

from src.schedule_manager import ScheduleManager
from src.kronox_scraper.kronox_scrape import runKronoxSearch

app = FastAPI()

VALID_SCHOOLS = [
    "hkr",
    "mau",
    "oru",
    # "ltu",
    "hig",
    # "sh",
    "hv",
    "hb",
    "mdh",
]
SCHOOL_BASE_URLS = {
    "hkr": "schema.hkr.se",
    "mau": "schema.mau.se",
    "oru": "schema.oru.se",
    # ! "ltu": "schema.ltu.se", COMPLETELY BLOCKED OFF BECAUSE LOGIN REQUIRED
    "hig": "schema.hig.se",
    # ! "sh": "kronox.sh.se", COMPLETELY BLOCKED OFF BECAUSE LOGIN REQUIRED
    "hv": "schema.hv.se",
    "hb": "schema.hb.se",
    "mdh": "webbschema.mdh.se",  # ! LOGIN REQUIRED FOR PROGRAMMES
    # Konstfack school on kronox' website, but can't find schedule page
}


@app.get("/testing")
async def root1():
    return "successfully accessed API!"


@app.get("/schedules/{id}")
async def scheduleQuery(
    id: str,
    school: str,
    year: str | None = Query(None),
    month: str | None = Query(None),
    day: str | None = Query(None),
) -> Dict:

    if school not in VALID_SCHOOLS:
        return Response(content="Invalid school query", status_code=404)

    startDate = "idag"
    if year and month and day:
        startDate = f"{year}-{month}-{day}"

    schedule = ScheduleManager(id, SCHOOL_BASE_URLS[school], startDate)

    if "error" in schedule.scheduleDict.keys():
        # return {"schedule": schedule.scheduleDict}
        return Response(content="Schedule not found error", status_code=404)

    return schedule.scheduleDict


@app.get("/schedules/search/")
async def searchSchedules(school: str, search: str | None = None):
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

    return {
        "requestedSchedule": runKronoxSearch(
            search, year, SCHOOL_BASE_URLS[school]
        )
    }

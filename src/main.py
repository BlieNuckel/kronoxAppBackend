import re
from typing import Dict
from fastapi import FastAPI, Query, Request, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.schedule_manager import ScheduleManager
from src.kronox_scraper.kronox_scrape import runKronoxSearch

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
        return schedule.scheduleDict
    else:
        return schedule.getFilteredSchedule(year, month, day)


@app.get("/schedules/search/")
@limiter.limit("40/minute")
async def searchSchedules(
    request: Request, school: str, search: str | None = None
):
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

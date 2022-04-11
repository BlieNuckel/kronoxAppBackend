from typing import Dict
from fastapi import FastAPI, Query

# from src.services.validity_checker import sortValid
from src.routes.schedule_getter import getSchedules
from src.routes.search_getter import searchSchedules

app = FastAPI()


@app.get("/testing")
async def root1():
    return "successfully accessed API!"


@app.get("/schedules/{id}")
async def scheduleQueryEndpoint(
    id: str,
    school: str,
    startTag: str | None = Query(None),
    year: str | None = Query(None),
    month: str | None = Query(None),
    day: str | None = Query(None),
) -> Dict:
    return getSchedules(id, school, startTag=startTag, year=year, month=month, day=day)


@app.get("/schedules/search/")
async def searchSchedulesEndpoint(school: str, search: str | None = Query(None)):
    return searchSchedules(school, search=search)

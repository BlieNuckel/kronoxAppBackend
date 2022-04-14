from typing import Dict
from fastapi import FastAPI, Query, Response
from src.exceptions.login_exceptions import LoginException
from src.models.registration import Registration
from src.models.user import User
from src.services.login_scraper.login import Login

# from src.services.validity_checker import sortValid
from src.routes.schedule_getter import getSchedules
from src.routes.search_getter import searchSchedules
from src.util.schools_info import SCHOOL_BASE_URLS, VALID_SCHOOLS

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
    print('MAIN')
    return getSchedules(id, school, startTag=startTag, year=year, month=month, day=day)


@app.get("/schedules/search/")
async def searchSchedulesEndpoint(school: str, search: str | None = Query(None)):
    return searchSchedules(school, search=search)


@app.post("/user/events")
async def getUserEventsEndpoint(user: User, school: str):
    if school not in VALID_SCHOOLS:
        return Response(content="Invalid school query", status_code=404)

    login = Login(user.username, user.password, SCHOOL_BASE_URLS[school])
    try:
        return login.getEvents()
    except LoginException:
        return Response(content="Error logging into user", status_code=403)


@app.post("/user/events/register")
async def registerUserEventEndpoint(registration: Registration, school: str):
    if school not in VALID_SCHOOLS:
        return Response(content="Invalid school query", status_code=404)

    login = Login(registration.username, registration.password, SCHOOL_BASE_URLS[school])
    login.register(registration.event_code)


@app.post("/user/events/unregister")
async def unregisterUserEventEndpoint(registration: Registration, school: str):
    if school not in VALID_SCHOOLS:
        return Response(content="Invalid school query", status_code=404)

    login = Login(registration.username, registration.password, SCHOOL_BASE_URLS[school])
    login.unregister(registration.event_code)

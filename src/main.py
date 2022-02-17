from fastapi import FastAPI
from schedule_manager import ScheduleManager

app = FastAPI()


@app.get("/testing")
async def root1():
    return "successfully accessed API!"


@app.get("/schedule/{id}")
async def scheduleGetter(id: str):
    schedule = ScheduleManager(id)
    return schedule.json

from fastapi import FastAPI

app = FastAPI()


@app.get("/testing")
async def root1():
    return "successfully accessed API!"


@app.get("/schedule/{id}")
async def scheduleGetter(id: str):
    return {"message": "Hello World"}

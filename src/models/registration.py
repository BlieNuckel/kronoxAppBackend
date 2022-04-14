from pydantic import BaseModel


class Registration(BaseModel):
    username: str
    password: str
    event_code: str

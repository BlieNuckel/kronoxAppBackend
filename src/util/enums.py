from datetime import datetime, timedelta
from enum import Enum


class StartDateEnum(Enum):
    today = "today"
    startOfWeek = "startOfWeek"

    def getDateValue(self) -> str:
        match self:
            case StartDateEnum.today:
                return "idag"
            case StartDateEnum.startOfWeek:
                currentTime = datetime.now()
                startOfWeekTimeStamp = currentTime - timedelta(days=currentTime.weekday())
                return startOfWeekTimeStamp.strftime("%Y-%m-%d")


class months(Enum):
    January = 1
    February = 2
    March = 3
    April = 4
    May = 5
    June = 6
    July = 7
    August = 8
    September = 9
    October = 10
    November = 11
    December = 12


class days(Enum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6

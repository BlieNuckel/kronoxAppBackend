import multiprocessing
from multiprocessing import Manager
from typing import Dict

from fastapi import Response

from src.services.login_scraper.user_event_spiders.register_spider import RegisterSpider
from src.services.login_scraper.user_event_spiders.unregister_spider import UnregisterSpider
from src.services.login_scraper.spider_executers import event_executers


class Login:
    def __init__(self, username: str, password: str, baseUrl: str) -> None:
        self.username = username
        self.password = password
        self.baseUrl = baseUrl

    def getEvents(self) -> Dict | Response:
        manager = Manager()
        sharedDict = manager.dict()

        p = multiprocessing.Process(
            target=event_executers._executeGetEventsSpider,
            args=[sharedDict, self.username, self.password, self.baseUrl],
        )
        p.start()
        p.join()

        if "error" in sharedDict.keys():
            return Response(content="Error logging into account", status_code=403)

        return sharedDict

    def unregister(self, event_code: str) -> Dict | Response:
        manager = Manager()
        sharedDict = manager.dict()

        p = multiprocessing.Process(
            target=event_executers._executeRegisterOrUnregisterEventSpider,
            args=[UnregisterSpider, sharedDict, self.username, self.password, self.baseUrl, event_code],
        )
        p.start()
        p.join()

        if "error" in sharedDict.keys():
            return Response(content="Error logging into account", status_code=403)

        return sharedDict

    def register(self, event_code: str) -> Dict | Response:
        manager = Manager()
        sharedDict = manager.dict()

        p = multiprocessing.Process(
            target=event_executers._executeRegisterOrUnregisterEventSpider,
            args=[RegisterSpider, sharedDict, self.username, self.password, self.baseUrl, event_code],
        )
        p.start()
        p.join()

        if "error" in sharedDict.keys():
            return Response(content="Error logging into account", status_code=403)

        return sharedDict

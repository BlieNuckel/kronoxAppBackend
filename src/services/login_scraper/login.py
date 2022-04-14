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

    def errHandler(self, exception: Exception):
        raise exception

    def getEvents(self) -> Dict | Response:
        manager = Manager()
        dict = manager.dict()

        p = multiprocessing.Process(
            target=event_executers._executeGetEventsSpider,
            args=[dict, self.username, self.password, self.baseUrl, self.errHandler],
        )
        p.start()
        p.join()

        return dict

    def unregister(self, event_code: str) -> Dict | Response:
        p = multiprocessing.Process(
            target=event_executers._executeRegisterOrUnregisterEventSpider,
            args=[UnregisterSpider, self.username, self.password, self.baseUrl, event_code],
        )
        p.start()
        p.join()

    def register(self, event_code: str) -> Dict | Response:
        p = multiprocessing.Process(
            target=event_executers._executeRegisterOrUnregisterEventSpider,
            args=[RegisterSpider, self.username, self.password, self.baseUrl, event_code],
        )
        p.start()
        p.join()

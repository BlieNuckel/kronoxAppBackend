from types import FunctionType
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher
from typing import Dict

from src.services.login_scraper.user_event_spiders.activities_spider import ActivitiesSpider
from src.services.login_scraper.user_event_spiders.register_spider import RegisterSpider
from src.services.login_scraper.user_event_spiders.unregister_spider import UnregisterSpider


def _executeGetEventsSpider(dict: Dict, username: str, password: str, baseUrl: str, errCallback: FunctionType):
    def crawler_callback(signal, sender, item, response, spider):
        dict.update(item)

    dispatcher.connect(crawler_callback, signal=signals.item_scraped)

    process = CrawlerProcess(install_root_handler=True)
    process.crawl(ActivitiesSpider, baseUrl, username, password, errCallback)
    process.start()
    process.join()


def _executeRegisterOrUnregisterEventSpider(
    spider: RegisterSpider | UnregisterSpider, username: str, password: str, baseUrl: str, event_code: str
):
    process = CrawlerProcess(install_root_handler=True)
    process.crawl(spider, baseUrl, username, password, event_code)
    process.start()
    process.join()

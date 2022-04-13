from scrapy.crawler import CrawlerProcess
from src.services.login_scraper.user_event_spiders.activities_spider import ActivitiesSpider
from src.services.login_scraper.user_event_spiders.register_spider import RegisterSpider
from src.services.login_scraper.user_event_spiders.unregister_spider import UnregisterSpider


class Login:
    def __init__(self, username: str, password: str, baseUrl: str) -> None:
        self.username = username
        self.password = password
        self.baseUrl = baseUrl

    def getEvents(self):
        process = CrawlerProcess(install_root_handler=False)
        process.crawl(ActivitiesSpider, self.baseUrl, self.username, self.password)
        process.start()
        process.join()

    def unregister(self, event_code: str):
        process = CrawlerProcess(install_root_handler=False)
        process.crawl(UnregisterSpider, self.baseUrl, self.username, self.password, event_code)
        process.start()
        process.join()

    def register(self, event_code: str):
        process = CrawlerProcess(install_root_handler=False)
        process.crawl(RegisterSpider, self.baseUrl, self.username, self.password, event_code)
        process.start()
        process.join()

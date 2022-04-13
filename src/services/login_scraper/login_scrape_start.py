import multiprocessing
from typing import List
from src.services.login_scraper.login import Login
from src.services.login_scraper.login_spider import LoginSpider
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher
from multiprocessing import Process


def runKronoxLogin(baseUrl: str, username: str, password: str) -> List:
    manager = multiprocessing.Manager()
    sharedResultList = manager.list()

    p = Process(
        target=__executeSpider,
        args=[sharedResultList, baseUrl, username, password],
    )
    p.start()
    p.join()
    return list(sharedResultList)


def __executeSpider(sharedResultList: List, baseUrl: str, username: str, password: str):
    def crawler_callback(signal, sender, item, response, spider):
        sharedResultList.append(item)

    dispatcher.connect(crawler_callback, signal=signals.item_scraped)

    process = CrawlerProcess()
    process.crawl(LoginSpider, baseUrl, username, password)
    process.start()
    process.join()


if __name__ == "__main__":
    login = Login("lasse_koordt_rosenkrans.poulsen0003@stud.hkr.se", "ZjqZj58CtuYvL2", "kronox.hkr.se")
    login.getEvents()

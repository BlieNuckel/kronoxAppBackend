import logging
import multiprocessing
from typing import List
from src.kronox_scraper.kronoxspider import KronoxSpider
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher
from multiprocessing import Process


def runKronoxSearch(searchQuery: str, yearQuery: str):
    manager = multiprocessing.Manager()
    sharedResultList = manager.list()

    p = Process(
        target=__executeSpider, args=[sharedResultList, searchQuery, yearQuery]
    )
    p.start()
    p.join()
    return list(sharedResultList)


def __executeSpider(sharedResultList: List, searchQuery: str, yearQuery: str):
    logging.getLogger("scrapy").propagate = False

    def crawler_callback(signal, sender, item, response, spider):
        sharedResultList.append(item)

    dispatcher.connect(crawler_callback, signal=signals.item_scraped)

    process = CrawlerProcess()
    process.crawl(KronoxSpider, searchQuery, yearQuery)
    process.start()
    process.join()

from typing import List
import scrapy
from scrapy.responsetypes import Response
from scrapy import Selector
import re

from src.ics_service import fetchIcsFile


class KronoxSpider(scrapy.Spider):
    name = "kronox"
    start_urls = ["https://kronox.hkr.se/program.jsp"]

    def __init__(self, searchString: str, yearQuery: str):
        self.searchString = searchString
        self.yearQuery = yearQuery
        super().__init__(self.name)

    def start_requests(self):
        return [
            scrapy.Request.from_curl(
                f"""curl "https://kronox.hkr.se/ajax/ajax_sokResurser.jsp?sokord={self.searchString}&startDatum=idag&slutDatum=&intervallTyp=m&intervallAntal=6"
  -H "authority: kronox.hkr.se"
  -H "accept: text/html, */*; q=0.01"
  -H "x-requested-with: XMLHttpRequest"
  -H "sec-ch-ua-mobile: ?0"
  -H "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
  -H "sec-ch-ua-platform: ^\^"Windows^\^""
  -H "sec-fetch-site: same-origin"
  -H "sec-fetch-mode: cors"
  -H "sec-fetch-dest: empty"
  -H "referer: https://kronox.hkr.se/index.jsp"
  -H "accept-language: en-DK,en-US;q=0.9,en;q=0.8,sv;q=0.7,nl;q=0.6"
  -H "cookie: _ga=GA1.2.78593240.1630837259; nmstat=07ac4e82-5236-e1ba-704f-855e5c518502; _ga=GA1.3.78593240.1630837259; _gid=GA1.3.1338770725.1645310517; JSESSIONID=Nui3Oy8S8ZGjCmUff8tIydnuVoR4xvFjHYdCFuHg.hkapp35"
  --compressed"""  # noqa
            )
        ]

    def parse(self, response: Response):

        results: List[Selector] = response.selector.xpath("/html/body/ul/li")
        for result in results:

            if (
                self.yearQuery
                in result.xpath("./table/tr/td[2]/a/text()").get()
            ):
                item = {}

                item["scheduleId"] = re.findall(
                    "&?resurser=(.*?)($|&)",
                    result.xpath("./table/tr/td[2]/a/@href").get(),
                )[0][0]

                item["scheduleName"] = self.stringUniqueWords(
                    result.xpath("./table/tr/td[2]/a/text()").get().split()
                )

                try:
                    fetchIcsFile(item["scheduleId"])
                    yield item
                except TypeError:
                    yield

    def stringUniqueWords(self, wordsToClean: Selector) -> str:
        words = wordsToClean
        seen = set()
        seen_add = seen.add

        def add(x):
            seen_add(x)
            return x

        return " ".join(add(i) for i in words if i not in seen)

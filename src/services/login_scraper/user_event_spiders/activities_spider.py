from datetime import datetime
import re
from typing import List
from scrapy import Request, Selector
from src.services.login_scraper.login_spider import LoginSpider
from scrapy.responsetypes import Response


class ActivitiesSpider(LoginSpider):
    def __init__(self, baseUrl: str, username: str, password: str):
        super().__init__(baseUrl, username, password)

    def onLoggedIn(self, response: Response):
        return Request.from_curl(
            f"""
                curl 'https://{self.baseUrl}/aktivitetsanmalan.jsp?'
                -H 'authority: {self.baseUrl}'
                -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
                -H 'accept-language: en-DK,en-US;q=0.9,en;q=0.8,sv;q=0.7,nl;q=0.6'
                -H 'referer: https://{self.baseUrl}/aktivitetsanmalan.jsp?'
                -H 'sec-ch-ua-mobile: ?0'
                -H 'sec-ch-ua-platform: "Windows"'
                -H 'sec-fetch-dest: document'
                -H 'sec-fetch-mode: navigate'
                -H 'sec-fetch-site: same-origin'
                -H 'sec-fetch-user: ?1'
                -H 'upgrade-insecure-requests: 1'
                -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'
                --compressed
            """,  # noqa
            callback=self.parse,
        )

    def parse(self, response: Response):
        result = {
            "registered": [],
            "available": [],
            "upcoming": [],
            "missed": [],
        }

        # inner_text: List[str] = response.selector.css(".tentamen-container").xpath("div/text()").getall()
        inner_texts: List[str] = response.selector.css(".tentamen-container").xpath("div/text()").getall()[2:]

        for index, text in enumerate(inner_texts):
            if text.strip() == "":
                event_divs: List[Selector] = response.selector.css(".tentamen-container").xpath(
                    "(div)"
                )[index].xpath("div")
                for event_div in event_divs:
                    event = {"event_code": ""}

                    date: str = ""

                    event["name"] = event_div.xpath("div/b/text()").get().strip()

                    inner_divs = event_div.xpath("div")
                    for inner_div in inner_divs:
                        if inner_div.xpath("a/@onclick"):
                            onclick_content = inner_div.xpath("a/@onclick").get().strip()
                            event["event_code"] = re.findall(r"anmal\('(.*)'(,false)?\)", onclick_content)[0][0]

                            continue

                        content = inner_div.xpath("text()").get()

                        if content is None:
                            continue

                        content = content.strip()

                        if content.lower().startswith("datum:"):
                            date = content.strip()[7:]
                        elif content.lower().startswith("start:"):
                            time_of_start = f"{date} {content.strip()[7:]}"
                            event["start"] = datetime.strptime(time_of_start, "%Y-%m-%d %H:%M").isoformat()
                        elif content.lower().startswith("slut:"):
                            time_of_end: str = f"{date} {content.strip()[6:]}"
                            event["end"] = datetime.strptime(time_of_end, "%Y-%m-%d %H:%M").isoformat()
                        elif content.lower().startswith("sista anmdatum"):
                            deadline_date: str = content.strip()[14:].strip()[2:]
                            event["deadline"] = datetime.strptime(deadline_date, "%Y-%m-%d").isoformat()
                        elif content.lower().startswith("typ:"):
                            event["type"] = content.strip()[5:]

                    match index:
                        case 0:
                            result["registered"].append(event)
                            continue
                        case 1:
                            result["available"].append(event)
                            continue
                        case 2:
                            result["upcoming"].append(event)
                            continue
                        case 3:
                            result["missed"].append(event)
                            continue
                        case _:
                            continue

        yield result

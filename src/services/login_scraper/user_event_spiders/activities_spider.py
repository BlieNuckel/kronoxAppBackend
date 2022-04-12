from scrapy import Request
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
                -H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"'
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

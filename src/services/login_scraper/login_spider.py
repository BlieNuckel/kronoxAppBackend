from types import FunctionType
from urllib.parse import quote
from scrapy.spiders.init import InitSpider
from scrapy import Request
from scrapy.responsetypes import Response

from src.exceptions.login_exceptions import LoginException


class LoginSpider(InitSpider):
    name = "login"

    def __init__(self, baseUrl: str, username: str, password: str, errCallback: FunctionType):
        self.baseUrl = baseUrl
        self.username = username
        self.password = password
        self.errCallback = errCallback
        super().__init__(self.name)

    def start_requests(self):
        return [
            Request.from_curl(
                f"""
                    curl "https://{self.baseUrl}/login_do.jsp"
                    -H "authority: {self.baseUrl}"
                    -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
                    -H "accept-language: en-DK,en-US;q=0.9,en;q=0.8,sv;q=0.7,nl;q=0.6"
                    -H "cache-control: max-age=0"
                    -H "content-type: application/x-www-form-urlencoded"
                    -H "origin: https://{self.baseUrl}"
                    -H "referer: https://{self.baseUrl}/index.jsp"
                    -H "sec-ch-ua: "Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100""
                    -H "sec-ch-ua-mobile: ?0"
                    -H "sec-ch-ua-platform: "Windows""
                    -H "sec-fetch-dest: document"
                    -H "sec-fetch-mode: navigate"
                    -H "sec-fetch-site: same-origin"
                    -H "sec-fetch-user: ?1"
                    -H "upgrade-insecure-requests: 1"
                    -H "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36"
                    --data-raw "username={quote(self.username)}&password={quote(self.password)}"
                    --compressed
                """,  # noqa
                callback=self.loginCheck,
                errback=self.errCallback,
            )
        ]

    def loginCheck(self, response: Response):
        if response.selector.css(".title::text").get().lower() == "inloggning misslyckades":
            raise LoginException

        return self.onLoggedIn(response)

    def parse(self, response: Response):
        print(response.text)

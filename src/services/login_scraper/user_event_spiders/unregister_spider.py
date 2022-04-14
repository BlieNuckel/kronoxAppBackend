from scrapy import Request
from src.services.login_scraper.login_spider import LoginSpider
from scrapy.responsetypes import Response


class UnregisterSpider(LoginSpider):
    def __init__(self, baseUrl: str, username: str, password: str, event_code: str):
        self.event_code = event_code
        super().__init__(baseUrl, username, password)

    def onLoggedIn(self, response: Response):
        return Request.from_curl(
            f"""
                curl 'https://{self.baseUrl}/ajax/ajax_aktivitetsanmalan.jsp?op=avanmal&deltagarMojlighetsId={self.event_code}'
                -H 'authority: {self.baseUrl}'
                -H 'accept: text/html, */*; q=0.01'
                -H 'accept-language: en-DK,en-US;q=0.9,en;q=0.8,sv;q=0.7,nl;q=0.6'
                -H 'referer: https://{self.baseUrl}/aktivitetsanmalan.jsp?'
                -H 'sec-ch-ua-mobile: ?0'
                -H 'sec-ch-ua-platform: "Windows"'
                -H 'sec-fetch-dest: empty'
                -H 'sec-fetch-mode: cors'
                -H 'sec-fetch-site: same-origin'
                -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'
                -H 'x-requested-with: XMLHttpRequest'
                --compressed
            """  # noqa
        )

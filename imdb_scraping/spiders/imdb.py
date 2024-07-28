import scrapy
from scrapy.crawler import CrawlerProcess


class ImdbSpider(scrapy.Spider):
    name = "imdb"
    # allowed_domains = ["imdb.com"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    def start_requests(self):
        url = "https://www.onthemarket.com/for-sale/property/uk"

        for i in range(1, 6):
            next_url = url + "/?page=" + str(i)
            yield scrapy.Request(
                url=next_url, headers=self.headers, callback=self.parse
            )

    def parse(self, response):
        pass


if __name__ == "__main__":
    # process = OnTheMarket()
    # process.parse("")

    process = CrawlerProcess()
    process.crawl(ImdbSpider)
    process.start()

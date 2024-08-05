import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import json
import time
# from scrapy_splash import SplashRequest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options


class ImdbSpider(scrapy.Spider):
    name = "imdb"
    # allowed_domains = ["imdb.com"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    custom_settings = {
        # 'FEED_FORMAT': 'csv',
        # 'FEED_URI': 'basic_scrapy/onthemarket.csv',
        "LOG_FILE": "logs/imdb.log"
    }

    base_url = "https://www.imdb.com"

    def __init__(self, *args, **kwargs):
        super(ImdbSpider, self).__init__(*args, **kwargs)

        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')

        # self.driver = webdriver.Chrome(service=ChromeService(
        #     ChromeDriverManager().install()), options=options)

    def start_requests(self):

        url = ImdbSpider.base_url + "/title/tt11152168/?ref_=sr_t_10"

        # for letter in alphabets:
        #     next_url = url + "?from=" + str(letter)
        #     break
        print(url)
        yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):

        # print("response.url---> ", response.url)
        # self.driver.get(response.url)

        # # visit each section
        # sections = self.driver.find_elements(By.TAG_NAME, 'section')
        # for section in sections:
        #     self.driver.execute_script("arguments[0].scrollIntoView();", section)
        #     time.sleep(0.3)

        # try:
        #     element = WebDriverWait(self.driver, 20).until(
        #         EC.presence_of_element_located(
        #             (By.CSS_SELECTOR, 'section[data-testid="Storyline"]'))
        #     )
        #     print("Element found!")
        # except Exception as e:
        #     print("Element not found within the given time")

        # body = self.driver.page_source

        html = ""
        with open("template.html", "r", encoding="utf-8") as html_file:
            # html_file.write(body)
            for line in html_file.read():
                html += line

        # self.driver.close()
        response = Selector(text=html)

        # to get movie title
        try:
            title = response.css("span.hero__primary-text::text").get()
        except Exception as e:
            title = None

        # to get movie run time
        try:
            run_time = (
                [response.css("div.sc-1f50b7c-0").css("ul").css("li")][-1]
                .css("li::text")
                .get()
            )
        except Exception as e:
            run_time = None

        # to get all top cast
        try:

            movie_cast_elements = response.css("section.sc-bfec09a1-0").css(
                "div.sc-bfec09a1-7"
            )

            top_cast = []
            for movie_cast_element in movie_cast_elements:
                try:
                    actor = movie_cast_element.css(
                        "a.sc-bfec09a1-1::text").get()
                except Exception as e:
                    actor = None

                try:
                    roles = [
                        span.css("span::text").get()
                        for span in movie_cast_element.css("span.sc-bfec09a1-4")
                    ]
                except Exception as e:
                    actor = None

                top_cast.append({"actor": actor, "roles": roles})

        except Exception as e:
            top_cast = []

        try:
            meta_cast_element = response.css('ul.sc-bfec09a1-8')

            meta_cast = {}
            for li in meta_cast_element.css('li'):
                span_text = li.css('span::text').get()
                if (span_text == 'Director'):
                    try:
                        _data = [_li.css('a::text').get() for _li in li.css(
                            'ul.ipc-metadata-list-item__list-content')]
                    except Exception as e:
                        _data = []
                    meta_cast['Director'] = _data
                elif (span_text == 'Writer'):
                    try:
                        _data = [_li.css('a::text').get() for _li in li.css(
                            'ul.ipc-metadata-list-item__list-content')]
                    except Exception as e:
                        _data = []
                    meta_cast['Writer'] = _data
                else:
                    pass
        except Exception as e:
            meta_cast = {}

        # plot summery
        try:
            plot_summery = response.css('span.sc-2d37a7c7-0::text').get()
        except Exception as e:
            plot_summery = None
        # print(storyline_ele)
        # plot_summery = storyline_ele.css('div.ipc-html-content-inner-div').get()
        # print(plot_summery)

        items = {
            "title": title,
            "plot_summery": plot_summery,
            "run_time": run_time,
            "top_cast":  top_cast
        }
        items = {**items, **meta_cast}
        # print(items)

        storyline_ul = response.css('ul.sc-20579f43-1')
        # print(storyline_ul)
        taglines_ele = storyline_ul.css('li[data-testid="storyline-taglines"]')

        taglines = [li.css('span::text').get()
                    for li in taglines_ele.css('ul').css('li')]
        print(taglines)

        genres_ele = storyline_ul.css('li[data-testid="storyline-genres"]')
        genres = [li.css('a::text').get()
                    for li in genres_ele.css('ul').css('li')]
        print(genres)
        
        certificate_ele = storyline_ul.css('li[data-testid="storyline-certificate"]')
        certificate = [li
                    for li in certificate_ele.css('ul').css('li')]
        print(certificate)

if __name__ == "__main__":
    # process = ImdbSpider()
    # process.parse("")
    # process.start_requests()

    process = CrawlerProcess()
    process.crawl(ImdbSpider)
    process.start()

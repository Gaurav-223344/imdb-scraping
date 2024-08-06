# import pandas as pd
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


class ImdbMovies:
    name = "imdb"
    # allowed_domains = ["imdb.com"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    base_url = "https://www.imdb.com"

    def __init__(self, file):
        self.file = file
        # self._driver = self._get_driver()

    def _get_driver(self) -> webdriver.Chrome:

        options = Options()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        # options.add_argument("--headless")
        # options.add_argument("--disable-gpu")
        # options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--allow-running-insecure-content")
        # options.add_argument("--disable-web-security")
        # options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument("--disable-infobars")
        # options.add_argument("--disable-extensions")
        # options.add_argument("--disable-popup-blocking")
        # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )
        return driver

    def run(self):
        self._start_requests()

    def _start_requests(self):
        with open(self.file, "r") as json_file:
            movies_dicts = json.load(json_file)
        for movie in movies_dicts:
            url = movie.get("url")
            self._parse(url)

    def _get_web_data_using_selenium_driver(self, url):
        print("url---> ", url)
        driver = self._get_driver()
        driver.get(url)

        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("Main content loaded.")
        except Exception as e:
            print(f"Main content not loaded within the given time: {e}")

        # visit each section
        sections = driver.find_elements(By.TAG_NAME, "section")

        for section in sections:
            try:
                driver.execute_script("arguments[0].scrollIntoView();", section)
            except:
                pass
            if len(sections) > 5:
                time.sleep(0.5)
            else:
                time.sleep(1)

        try:
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'section[data-testid="Storyline"]')
                )
            )
            print("Element found!")
        except Exception as e:
            print("Element not found within the given time")

        body = driver.page_source
        driver.quit()
        return body

    def _parse(self, url):

        body = self._get_web_data_using_selenium_driver(url)

        soup = BeautifulSoup(body, "html.parser")
        # response = Selector(text=body)

        # to get movie title
        title = None
        h1_tag = soup.find("h1", {"data-testid": "hero__pageTitle"})

        if h1_tag:
            title = h1_tag.find("span").get_text()
        print(title)

        # # to get movie run time

        # run_time = (
        #     [response.css("div.sc-1f50b7c-0").css("ul").css("li")][-1]
        #     .css("li::text")
        #     .get()
        # )

        # # to get all top cast
        # try:

        #     movie_cast_elements = response.css("section.sc-bfec09a1-0").css(
        #         "div.sc-bfec09a1-7"
        #     )

        #     top_cast = []
        #     for movie_cast_element in movie_cast_elements:
        #         try:
        #             actor = movie_cast_element.css("a.sc-bfec09a1-1::text").get()
        #         except Exception as e:
        #             actor = None

        #         try:
        #             roles = [
        #                 span.css("span::text").get()
        #                 for span in movie_cast_element.css("span.sc-bfec09a1-4")
        #             ]
        #         except Exception as e:
        #             actor = None

        #         top_cast.append({"actor": actor, "roles": roles})

        # except Exception as e:
        #     top_cast = []

        # try:
        #     meta_cast_element = response.css("ul.sc-bfec09a1-8")

        #     meta_cast = {}
        #     for li in meta_cast_element.css("li"):
        #         span_text = li.css("span::text").get()
        #         if span_text == "Director":
        #             try:
        #                 _data = [
        #                     _li.css("a::text").get()
        #                     for _li in li.css("ul.ipc-metadata-list-item__list-content")
        #                 ]
        #             except Exception as e:
        #                 _data = []
        #             meta_cast["Director"] = _data
        #         elif span_text == "Writer":
        #             try:
        #                 _data = [
        #                     _li.css("a::text").get()
        #                     for _li in li.css("ul.ipc-metadata-list-item__list-content")
        #                 ]
        #             except Exception as e:
        #                 _data = []
        #             meta_cast["Writer"] = _data
        #         else:
        #             pass
        # except Exception as e:
        #     meta_cast = {}

        # # plot summery
        # try:
        #     plot_summery = response.css("span.sc-2d37a7c7-0::text").get()
        # except Exception as e:
        #     plot_summery = None
        # # print(storyline_ele)
        # # plot_summery = storyline_ele.css('div.ipc-html-content-inner-div').get()
        # # print(plot_summery)

        # storyline_ul = response.css("ul.sc-20579f43-1")
        # # print(storyline_ul)
        # taglines_ele = storyline_ul.css('li[data-testid="storyline-taglines"]')

        # taglines = [
        #     li.css("span::text").get() for li in taglines_ele.css("ul").css("li")
        # ]

        # genres_ele = storyline_ul.css('li[data-testid="storyline-genres"]')
        # genres = [li.css("a::text").get() for li in genres_ele.css("ul").css("li")]

        # certificate_ele = storyline_ul.css('li[data-testid="storyline-certificate"]')
        # certificate = [
        #     li.css("span::text").get() for li in certificate_ele.css("ul").css("li")
        # ]

        # details_div = response.css('div[data-testid="title-details-section"]')

        # release_date_ele = details_div.css(
        #     'li[data-testid="title-details-releasedate"]'
        # )
        # release_date = [
        #     li.css("a::text").get() for li in release_date_ele.css("ul").css("li")
        # ]

        # origin_ele = details_div.css('li[data-testid="title-details-origin"]')
        # origin = [li.css("a::text").get() for li in origin_ele.css("ul").css("li")]

        # languages_ele = details_div.css('li[data-testid="title-details-languages"]')
        # languages = [
        #     li.css("a::text").get() for li in languages_ele.css("ul").css("li")
        # ]

        # filming_locations_ele = details_div.css(
        #     'li[data-testid="title-details-filminglocations"]'
        # )
        # filming_locations = [
        #     li.css("a::text").get() for li in filming_locations_ele.css("ul").css("li")
        # ]

        # companies_ele = details_div.css('li[data-testid="title-details-companies"]')
        # companies = [
        #     li.css("a::text").get() for li in companies_ele.css("ul").css("li")
        # ]

        # items = {
        #     "title": title,
        #     "plot_summery": plot_summery,
        #     "run_time": run_time,
        #     "top_cast": top_cast,
        #     "taglines": taglines,
        #     "genres": genres,
        #     "certificate": certificate,
        #     "release_date": release_date,
        #     "origin": origin,
        #     "languages": languages,
        #     "filming_locations": filming_locations,
        #     "companies": companies,
        # }

        # items = {**items, **meta_cast}
        # print(items)
        # yield items

    # def __del__(self):
    #     self._driver.quit()


if __name__ == "__main__":

    file = os.path.join("data", "movies_list_1900.json")
    process = ImdbMovies(file)
    process.run()

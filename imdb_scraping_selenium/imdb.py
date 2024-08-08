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

    def __init__(self, file, output_path):
        self._output_path = output_path
        self._file = file
        self._items = []
        # self._driver = None
        self._driver = self._get_driver()

    def _get_driver(self) -> webdriver.Chrome:

        options = Options()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        service = ChromeService(executable_path=ChromeDriverManager().install())

        driver = webdriver.Chrome(
            service=service, options=options
        )
        return driver

    def run(self):
        self._start_requests()

    def _start_requests(self):
        with open(self._file, "r") as json_file:
            movies_dicts = json.load(json_file)
        for movie in movies_dicts:
            url = movie.get("url")
            self._parse(url)
        self._save_in_json(self._output_path, self._items )
        
    def _get_web_data_using_selenium_driver(self, url):
        print("url---> ", url)
        driver = self._driver
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

        # # scroll through the page
        # scroll_step = 100
        # wait_time = 0.1
        # document_height = driver.execute_script("return document.body.scrollHeight")
        # scroll_position = 0

        # while scroll_position < document_height:
        #     driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        #     time.sleep(wait_time)
        #     scroll_position += scroll_step
        #     document_height = driver.execute_script("return document.body.scrollHeight")

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
        # driver.quit()
        return body

    def _get_title(self, soup: BeautifulSoup):
        # to get movie title
        title = None
        try:
            h1_tag = soup.find("h1", {"data-testid": "hero__pageTitle"})
            if h1_tag:
                title = h1_tag.find("span").get_text()
        except:
            title = None

        return title

    def _get_run_time(self, soup: BeautifulSoup):
        try:
            div = soup.find("div", class_="sc-1f50b7c-0")
            ul = div.find("ul")
            li_elements = ul.find_all("li")
            run_time = li_elements[-1].get_text()
        except AttributeError:
            run_time = None
        return run_time

    def _get_top_cast(self, soup: BeautifulSoup):
        try:
            section = soup.find("section", class_="sc-bfec09a1-0")
            movie_cast_elements = section.find_all("div", class_="sc-bfec09a1-7")

            top_cast = []
            for movie_cast_element in movie_cast_elements:
                try:
                    actor = movie_cast_element.find(
                        "a", class_="sc-bfec09a1-1"
                    ).get_text()
                except AttributeError:
                    actor = None

                try:
                    roles = [
                        span.get_text()
                        for span in movie_cast_element.find_all(
                            "span", class_="sc-bfec09a1-4"
                        )
                    ]
                except AttributeError:
                    roles = None

                top_cast.append({"actor": actor, "roles": roles})

        except AttributeError:
            top_cast = []
        return top_cast

    def _get_meta_cast(self, soup: BeautifulSoup):
        try:
            meta_cast_element = soup.find("ul", class_="sc-bfec09a1-8")

            meta_cast = {}

            for li in meta_cast_element.find_all("li"):
                span_element = li.find("span", class_="ipc-metadata-list-item__label")
                if span_element:
                    span_text = span_element.get_text()
                else:
                    continue

                if span_text == "Director" or span_text == "Writer":
                    try:
                        _data = [
                            _li.find("a").get_text()
                            for _li in li.find(
                                "ul", class_="ipc-metadata-list-item__list-content"
                            ).find_all("li")
                        ]
                    except AttributeError as e:
                        _data = []
                    meta_cast[span_text] = _data
                else:
                    pass

        except AttributeError:
            meta_cast = {}
            print("Elements not found or structure is different from expected")
        return meta_cast

    def _get_plot_summery(self, soup: BeautifulSoup):
        try:
            plot_summary = soup.find("span", class_="sc-2d37a7c7-0").get_text()
        except AttributeError:
            plot_summary = None
        return plot_summary

    def _get_taglines(self, storyline_ul: BeautifulSoup):
        try:
            taglines_ele = storyline_ul.find(
                "li", {"data-testid": "storyline-taglines"}
            )
            taglines = [li.get_text() for li in taglines_ele.find("ul").find_all("li")]
        except AttributeError:
            taglines = []
        return taglines

    def _get_genres(self, storyline_ul: BeautifulSoup):
        try:
            genres_ele = storyline_ul.find("li", {"data-testid": "storyline-genres"})
            genres = [li.get_text() for li in genres_ele.find("ul").find_all("li")]
        except AttributeError:
            genres = []
        return genres

    def _get_certificates(self, storyline_ul: BeautifulSoup):
        try:
            certificate_ele = storyline_ul.find(
                "li", {"data-testid": "storyline-certificate"}
            )
            certificate = [
                li.get_text() for li in certificate_ele.find("ul").find_all("li")
            ]
        except AttributeError:
            certificate = []
        return certificate

    def _get_storyline_data(self, soup: BeautifulSoup):
        storyline_ul = soup.find("ul", class_="sc-20579f43-1")
        storyline_data = {}
        if storyline_ul:
            storyline_data["taglines"] = self._get_taglines(storyline_ul)
            storyline_data["genres"] = self._get_genres(storyline_ul)
            storyline_data["certificate"] = self._get_certificates(storyline_ul)

        return storyline_data

    def _get_release_date(self, details_div: BeautifulSoup):
        try:
            release_date_ele = details_div.find(
                "li", {"data-testid": "title-details-releasedate"}
            )
            release_date = [
                li.get_text() for li in release_date_ele.find("ul").find_all("li")
            ]
        except AttributeError:
            release_date = []
        return release_date

    def _get_origin(self, details_div: BeautifulSoup):
        try:
            origin_ele = details_div.find("li", {"data-testid": "title-details-origin"})
            origin = [li.get_text() for li in origin_ele.find("ul").find_all("li")]
        except AttributeError:
            origin = []
        return origin

    def _get_languages(self, details_div: BeautifulSoup):
        try:
            languages_ele = details_div.find(
                "li", {"data-testid": "title-details-languages"}
            )
            languages = [
                li.get_text() for li in languages_ele.find("ul").find_all("li")
            ]
        except AttributeError:
            languages = []
        return languages

    def _get_filming_locations(self, details_div: BeautifulSoup):
        try:
            filming_locations_ele = details_div.find(
                "li", {"data-testid": "title-details-filminglocations"}
            )
            filming_locations = [
                li.get_text() for li in filming_locations_ele.find("ul").find_all("li")
            ]
        except AttributeError:
            filming_locations = []
        return filming_locations

    def _get_companies(self, details_div: BeautifulSoup):
        try:
            companies_ele = details_div.find(
                "li", {"data-testid": "title-details-companies"}
            )
            companies = [
                li.get_text() for li in companies_ele.find("ul").find_all("li")
            ]
        except AttributeError:
            companies = []
        return companies

    def _get_movie_details_data(self, soup: BeautifulSoup):
        details_div = soup.find("div", {"data-testid": "title-details-section"})
        details = {}
        if details_div:
            details["release_date"] = self._get_release_date(details_div)
            details["origin"] = self._get_origin(details_div)
            details["languages"] = self._get_languages(details_div)
            details["filming_locations"] = self._get_filming_locations(details_div)
            details["companies"] = self._get_companies(details_div)

        return details

    def _save_in_json(self, file_path, data):
        with open(file_path, "w", encoding="utf-8") as json_file:
            json_file.write(json.dumps(data))

    def _parse(self, url):

        body = self._get_web_data_using_selenium_driver(url)
        # body = ""
        # with open("template.html", "r", encoding="utf-8") as html_file:
        #     # html_file.write(body)
        #     for line in html_file.read():
        #         body += line

        soup = BeautifulSoup(body, "html.parser")
        title = self._get_title(soup)
        run_time = self._get_run_time(soup)
        top_cast = self._get_top_cast(soup)
        meta_cast = self._get_meta_cast(soup)
        plot_summery = self._get_plot_summery(soup)
        storyline_data = self._get_storyline_data(soup)
        movie_details_data = self._get_movie_details_data(soup)

        item = {
            "title": title,
            "plot_summery": plot_summery,
            "run_time": run_time,
            "top_cast": top_cast,
        }

        item = {**item, **meta_cast, **storyline_data, **movie_details_data}
        self._items.append(item)

    # def __del__(self):
    #     self._driver.quit()


if __name__ == "__main__":

    file = os.path.join("data", "movies_list_1900.json")
    process = ImdbMovies(file)
    process.run()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import json
from bs4 import BeautifulSoup
import math
import os

class ExtractMoviesFromIMDB:

    def __init__(self, year) -> None:
        self.year = year
        self._base_url = 'https://www.imdb.com'

    def _get_no_of_clicks(self, data):
        a, b = data.split("of")
        _, no_of_card_per_req = a.strip().split("-")
        total_no_of_card = b.replace(",", "")
        return math.ceil(int(total_no_of_card) / int(no_of_card_per_req))

    def extract_data(self, html_content, path):
        soup = BeautifulSoup(html_content, "html.parser")
        ul = soup.find('ul', class_='ipc-metadata-list')
        cards = ul.find_all('li')
        items = []
        for card in cards:
            title = card.find('div', class_='ipc-title').text
            url = self._base_url + \
                card.find('div', class_='ipc-title').find('a').get('href')
            items.append(
                {
                    "title": title,
                    "url": url
                }
            )

        with open(path, 'w', encoding='utf-8') as json_file:
            json_file.write(json.dumps(items))

    def run(self):
        driver = webdriver.Chrome(service=ChromeService(
            ChromeDriverManager().install()))

        url = f'{self._base_url}/search/title/?title_type=feature&release_date={self.year}-01-01,{self.year}-12-31'
        driver.get(url)
        time.sleep(5)

        # self.extract_data(driver.page_source, path)

# if __name__ == '__main__':
#     extract = ExtractMoviesFromIMDB(1940)
#     print(extract.run())

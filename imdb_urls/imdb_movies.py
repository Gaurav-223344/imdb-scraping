from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import time
import json
from bs4 import BeautifulSoup
import math
import os

class ExtractMoviesListFromIMDB:

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
        driver = self._get_driver()

        url = f'{self._base_url}/search/title/?title_type=feature&release_date={self.year}-01-01,{self.year}-12-31'
        driver.get(url)
        # return url
        time.sleep(10)
        div_element = driver.find_element(By.CLASS_NAME, 'jfNgiQ')
        total_movies_data = div_element.text
        no_of_clicks = self._get_no_of_clicks(total_movies_data)

        try:
            span = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'ipc-see-more'))
            )

            # Find the button within the span element
            button = span.find_element(By.TAG_NAME, 'button')
            for _ in range(no_of_clicks):
                driver.execute_script(
                    "window.scrollTo(arguments[0], arguments[1]);", button.location['x'], button.location['y'] - 100)
                time.sleep(1)
                button.click()
                time.sleep(3)

        except Exception as e:
            print(e)

        path = os.path.join('data', f'movies_list_{self.year}.json')
        body = driver.page_source
        self.extract_data(body, path)

# if __name__ == '__main__':
#     extract = ExtractMoviesListFromIMDB(1940)
#     print(extract.run())

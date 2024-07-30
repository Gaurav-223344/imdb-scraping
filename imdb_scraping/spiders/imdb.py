import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import json
class ImdbSpider(scrapy.Spider):
    name = "imdb"
    # allowed_domains = ["imdb.com"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    
    custom_settings = {
        # 'FEED_FORMAT': 'csv',
        # 'FEED_URI': 'basic_scrapy/onthemarket.csv',
        'LOG_FILE': 'basic_scrapy/onthemarket.log'
    }
    
    
    base_url = 'https://characterprofile.fandom.com'
    

    def start_requests(self):
        alphabets= "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        url = ImdbSpider.base_url + "/wiki/Category:Anime/Manga_Characters"

        for letter in alphabets:
            next_url = url + "?from=" + str(letter)
            break
        print(next_url)
        # yield scrapy.Request(
        #     url=next_url, headers=self.headers, callback=self.parse
        # )

    def parse(self, response):
        html = ""
        with open('template.html', 'r', encoding='utf-8') as html_file:
            # html_file.write(response.text)
            for line in html_file.read():
                html += line
        
        response = Selector(text=html)
        
        character_element_lists = response.css("li.category-page__member")
        character_element = character_element_lists[0]
        # print(character_element.css("a.category-page__member-link::text").get())
        print(character_element.css("a.category-page__member-link"))
        print(character_element.css("a.category-page__member-link::attr('href')").get())
        items = {
            "title" : str(character_element.css("a.category-page__member-link")).strip(),
            "url" : ImdbSpider.base_url + str(character_element.css("a.category-page__member-link::attr('href')").get()).strip()
        }

        print(json.dumps(items))
    
if __name__ == "__main__":
    process = ImdbSpider()
    process.parse("")
    # process.start_requests()

    # process = CrawlerProcess()
    # process.crawl(ImdbSpider)
    # process.start()

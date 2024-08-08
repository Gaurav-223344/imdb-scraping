import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import json
import time

# import pandas as pd
import os

from scrapy_splash import SplashRequest


class ImdbSpider(scrapy.Spider):
    name = "imdb"
    # allowed_domains = ["imdb.com"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    base_url = "https://www.imdb.com"

    def __init__(self, file, *args, **kwargs):
        super(ImdbSpider, self).__init__(*args, **kwargs)
        self.file = file

    def _get_lua_script(self):
        return """
            function scroll_all_section(splash)
                -- Get all sections
                local ok, sections = splash:runjs('return Array.from(document.getElementsByTagName("section"))')
                if not ok then
                    return splash:html() -- Return current HTML in case of failure
                end
                
                if not sections then
                    splash:log('No sections found.')
                    return
                end

                -- Scroll into view for each section
                for i, section in ipairs(sections) do
                    splash:runjs(string.format('arguments[0].scrollIntoView();', section))
                    -- Adjust wait time based on the number of sections
                    if #sections > 5 then
                    splash:wait(0.5)
                    else
                    splash:wait(1)
                    end
                end
            end

            function wait_for_element(splash, css, maxwait)
                -- Wait until a selector matches an element
                -- in the page. Return an error if waited more
                -- than maxwait seconds.
                if maxwait == nil then
                    maxwait = 10
                end
                return splash:wait_for_resume(string.format([[
                    function main(splash) {
                    var selector = '%s';
                    var maxwait = %s;
                    var end = Date.now() + maxwait*1000;

                    function check() {
                        if(document.querySelector(selector)) {
                        splash.resume('Element found');
                        } else if(Date.now() >= end) {
                        var err = 'Timeout waiting for element';
                        splash.error(err + " " + selector);
                        } else {
                        setTimeout(check, 200);
                        }
                    }
                    check();
                    }
                ]], css, maxwait))
            end

            function main(splash, args)
                splash:set_viewport_size(1920, 1080)
                splash:set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
                splash:go("https://www.imdb.com/title/tt23468450/?ref_=sr_t_1")
                splash:wait(1) -- Wait for the page to fully load
                wait_for_element(splash, "body", 30)
                scroll_all_section(splash)
                wait_for_element(splash, "section[data-testid=\"Storyline\"]", 30)
                return splash:html()
            end

            """

    def start_requests(self):

        # url = ImdbSpider.base_url + "/title/tt11152168/?ref_=sr_t_10"

        # for letter in alphabets:
        #     next_url = url + "?from=" + str(letter)
        #     break
        # file = os.path.join("data", "movies_list_1900.json")
        with open(self.file, "r") as json_file:
            movies_dicts = json.load(json_file)
        # df = pd.read_csv(file)
        for movie in movies_dicts:
            url = movie.get("url")
            print("movie url: ", url)
            break
        yield SplashRequest(
            url,
            self.parse,
            endpoint="execute",
            args={
                'wait': 3,  
                'timeout': 60,
                "lua_source": self._get_lua_script()
            },
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )

    def parse(self, response):
        page = response.meta["splash"]["args"]["url"]
        print("page--- ",page)
        filename = os.path.join("new_template.html")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.data["html"])
        print(f"Saved file {filename}")
        # html = ""
        # with open("template.html", "r", encoding="utf-8") as html_file:
        #     # html_file.write(body)
        #     for line in html_file.read():
        #         html += line

        # response = Selector(text=body)

    # def __del__(self):
    #     self._driver.quit()


if __name__ == "__main__":
    # process = ImdbSpider()
    # process.parse("")
    # process.start_requests()

    file = os.path.join("data", "movies_list_2024.json")
    process = CrawlerProcess()
    process.crawl(ImdbSpider, file=file)
    process.start()

from imdb_urls import ExtractMoviesListFromIMDB
from imdb_scraping import ImdbSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils import project
from imdb_scraping_selenium.imdb import ImdbMovies
import os

# if __name__ == "__main__":
#     year = 2024
#     create_new = False

#     file = os.path.join("data", f"movies_list_{year}.json")
#     file_exists = os.path.exists(file)

#     # if (create_new or (not file_exists)):
#     #     print("Extracting list of movies...")
#     #     extract = ExtractMoviesListFromIMDB(year)
#     #     extract.run()
#     #     print("Extraction of movies completed successfully")

#     custom_settings = {
#         "FEED_FORMAT": "csv",
#         "FEED_URI": f"data/movies_details_{year}.csv",
#         "LOG_FILE": "logs/imdb.log",
#         "SPLASH_URL": "http://localhost:8050",
#         "DOWNLOADER_MIDDLEWARES": {
#             "scrapy_splash.SplashCookiesMiddleware": 723,
#             "scrapy_splash.SplashMiddleware": 725,
#             "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
#         },
#         "SPIDER_MIDDLEWARES": {
#             "scrapy_splash.SplashDeduplicateArgsMiddleware": 100,
#         },
#         "DUPEFILTER_CLASS": "scrapy_splash.SplashAwareDupeFilter",
#         "HTTPCACHE_STORAGE": "scrapy_splash.SplashAwareFSCacheStorage",
#         "DEFAULT_REQUEST_HEADERS" : {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         },
#         "SPLASH_COOKIES_ENABLED" : True,
#         "SPLASH_CACHE_STORAGE" : 'scrapy_splash.SplashAwareFSCacheStorag'
#     }

#     settings = project.get_project_settings()
#     settings.update(custom_settings)
#     process = CrawlerProcess(settings=settings)
#     # process = CrawlerProcess()
#     process.crawl(ImdbSpider, file=file)
#     process.start()


def main():
    year = 1901
    create_new = False
    file = os.path.join("data", f"movies_list_{year}.json")
    file_exists = os.path.exists(file)

    if (create_new or (not file_exists)):
        print("Extracting list of movies...")
        extract = ExtractMoviesListFromIMDB(year)
        extract.run()
        print("Extraction of movies completed successfully")
    file = os.path.join("data", f"movies_list_{year}.json")
    output_path = os.path.join("data", f"movies_details_{year}.json")
    process = ImdbMovies(file, output_path)
    process.run()


if __name__ == "__main__":
    main()

from imdb_urls import ExtractMoviesListFromIMDB
from imdb_scraping import ImdbSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils import project 
import os

if __name__ == "__main__":
    year = 1900
    create_new = False

    file = os.path.join("data", f"movies_list_{year}.json")
    file_exists = os.path.exists(file)

    if (create_new or (not file_exists)):
        print("Extracting list of movies...")
        extract = ExtractMoviesListFromIMDB(year)
        extract.run()
        print("Extraction of movies completed successfully")
        
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': f'data/movies_details_{year}.csv',
        "LOG_FILE": "logs/imdb.log"
    }
    
    settings = project.get_project_settings()
    settings.update(custom_settings)
    process = CrawlerProcess(settings=settings)
    # process = CrawlerProcess()
    process.crawl(ImdbSpider, file=file)
    process.start()

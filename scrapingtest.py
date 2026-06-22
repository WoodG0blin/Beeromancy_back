import logging

#from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, unquote
import scrapy
from scrapy.crawler import CrawlerProcess

def parse_beer_rf(response):
    print("parsing beer.rf")

def parse_grainrus(response):
    print("parsing grainrus")

PARSING_CONFIG = {
    'beer_rf':{
            'start_urls': ["https://бир.рф/shop/grain/malt/"],
            'parse_function': parse_beer_rf
    },
    'grainrus':{
            'start_urls': ["https://grainrus.com/"],
            'parse_function': parse_grainrus
    }
}


class CyrillicUrlMiddleware:
    def _decode_url(self, url):
        """Внутренний метод для конвертации URL в кириллицу"""
        try:
            parsed_url = urlparse(url)
            cyrillic_netloc = parsed_url.netloc.encode('utf-8').decode('idna')
            cyrillic_path = unquote(parsed_url.path)
            cyrillic_query = unquote(parsed_url.query)
            
            return urlunparse(parsed_url._replace(
                netloc=cyrillic_netloc,
                path=cyrillic_path,
                query=cyrillic_query
            ))
        except Exception:
            return url

    def process_response(self, request, response, spider):
        response._set_url(self._decode_url(response.url))
        return response


class Scraper(scrapy.Spider):
    name = "scraper"
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'COOKIES_ENABLED': True,
        'DOWNLOADER_MIDDLEWARES': { '__main__.CyrillicUrlMiddleware': 543, },
        'DOWNLOAD_DELAY': 1.5, 
    }
    

    async def start(self):
        print("starting request")
        sites = ['beer_rf', 'grainrus']
        start_urls = ["https://бир.рф/shop/grain/malt/",
                    "https://pikabu.ru/",
                    "https://grainrus.com/"
                    ]
        
        for site in sites:
            if site not in PARSING_CONFIG:
                raise ValueError(f"Site '{site}' is not defined in PARSING_CONFIG")
            for url in PARSING_CONFIG[site]['start_urls']:
                yield scrapy.Request(url=url, callback=PARSING_CONFIG[site]['parse_function'])



def main():
    logging.getLogger('scrapy').setLevel(logging.WARNING)
    logging.getLogger('scrapy').propagate = False
    process = CrawlerProcess()
    process.crawl(Scraper)
    process.start()

if __name__ == "__main__":
    main()
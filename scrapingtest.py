import logging

from urllib.parse import urlparse, urlunparse, unquote
import scrapy
from scrapy.crawler import CrawlerProcess
from parsers import PARSING_CONFIG, ContentController

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
        'FEEDS': { 'outputs/products_data.json': {'format': 'json', 'encoding': 'utf8', 'overwrite': True} },
        'COOKIES_ENABLED': True,
        'DOWNLOADER_MIDDLEWARES': { '__main__.CyrillicUrlMiddleware': 543, },
        'DOWNLOAD_DELAY': 1.5, 
    }
    

    async def start(self):
        print("starting request")
        sites = ['beer_rf', 'grainrus']
        
        content_controller = ContentController()

        for product, config in PARSING_CONFIG.items():
            for site in config.values():
                parser = site['parser_class'](content_controller)
                for url in site['start_urls']:
                    yield scrapy.Request(url=url, callback=parser.parse, cb_kwargs={'item': product()})
        


def main():
    logging.getLogger('scrapy').setLevel(logging.WARNING)
    logging.getLogger('scrapy').propagate = False
    process = CrawlerProcess()
    process.crawl(Scraper)
    process.start()

if __name__ == "__main__":
    main()
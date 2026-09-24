import logging
from pathlib import Path

import scrapy
from scrapy.crawler import CrawlerProcess

from . import PARSING_CONFIG
from .content_controller import ContentController


class Scraper(scrapy.Spider):
    name = "scraper"
    def __init__(self, data_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_controller = ContentController(data_path)

    async def start(self):
        for product, config in PARSING_CONFIG.items():
            for site in config.values():
                parser = site['parser_class'](self.content_controller)
                for url in site['start_urls']:
                    yield scrapy.Request(url=url, callback=parser.parse, cb_kwargs={'item': product()})
        

def run_parsers(data_path: Path) -> None:
    logging.getLogger('scrapy').setLevel(logging.WARNING)
    logging.getLogger('scrapy').propagate = False

    logger = logging.getLogger(__name__)

    data_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        logger.info("Starting parsers")

        process = CrawlerProcess(settings={
                    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'FEEDS': { str(data_path): {'format': 'json', 'encoding': 'utf8', 'overwrite': True} },
                    'COOKIES_ENABLED': True,
                    'DOWNLOADER_MIDDLEWARES': { f"{__package__}.cyrillic_middleware.CyrillicUrlMiddleware": 543, },
                    'DOWNLOAD_DELAY': 1.5, 
                })

        #crawl() before start(): spider's __init__ reads data with content_controller, while start() overwrites it for FEEDS
        process.crawl(Scraper, data_path=str(data_path))
        process.start()

        logger.info(f"Scraping completed, output file: {data_path}")
    except Exception:
        logger.exception("Error occurred during scraping")
        raise
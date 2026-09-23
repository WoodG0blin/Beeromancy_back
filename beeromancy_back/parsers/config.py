from . import scrape_items
from .parser_classes import BeerRfParser, GrainrusHopsParser, GrainrusParser

PARSING_CONFIG = {
    scrape_items.MaltItem:{
        'beer_rf':{
            'start_urls': ["https://бир.рф/shop/grain/malt/"],
            'parser_class': BeerRfParser
        },
        'grainrus':{
            'start_urls': ["https://malt.ru/catalog/solod/"],
            'parser_class': GrainrusParser
        }
    },
    scrape_items.HopItem:{
        'beer_rf':{
            'start_urls': ["https://бир.рф/shop/hops/"],
            'parser_class': BeerRfParser
        },
        'grainrus':{
            'start_urls': ["https://malt.ru/catalog/khmel/"],
            'parser_class': GrainrusHopsParser
        }
    },
    scrape_items.YeastItem:{
        'beer_rf':{
            'start_urls': ["https://бир.рф/shop/yeast/"],
            'parser_class': BeerRfParser
        },
        'grainrus':{
            'start_urls': ["https://malt.ru/catalog/drozhzhi/"],
            'parser_class': GrainrusParser
        }
    }
}
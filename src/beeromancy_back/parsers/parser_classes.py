from abc import ABC, abstractmethod

from scrapy.loader import ItemLoader

from .content_controller import ContentController


def get_clean_string(value):
    return " ".join(get_clean_list(value))


def get_clean_list(value):
    return [str(i).strip() for i in value if i]


class BaseLoader(ItemLoader):
    default_output_processor = get_clean_string
    characteristics_out = get_clean_list


class Parser(ABC):
    def __init__(self, content_controller: ContentController):
        self.content_controller = content_controller

    @abstractmethod
    def parse(self, response, item):
        pass

class BeerRfParser(Parser):

    def parse(self, response, item):
        loader = BaseLoader(item)
        loader.add_value('source_domain', 'beer.rf')
        loader.add_value('currency', 'RUB')
        base_item = loader.load_item()

        yield from self.parse_page(response, base_item)

        pages = response.css('.plist > a > *::text').getall()
        try:
            last_page = int(pages[-1])
        except ValueError:
            last_page = 1

        if last_page > 1:
            pages_urls = [f"{response.url};{page}" for page in range(2, last_page + 1)]
            for page in pages_urls:
                yield response.follow(url=page, callback=self.parse_page, cb_kwargs={'item': base_item})

        
    def parse_page(self, response, item):
        product_cards = response.xpath('//div[@itemprop="itemListElement"]')
        for card in product_cards:
            item_loader = BaseLoader(item=item.copy(), response=response, selector=card)
            item_loader.add_xpath('name', './/*[@itemprop="name"]/text()')
            item_loader.add_xpath('price', './/*[@itemprop="price"]/@content')
            
            url = card.xpath('.//*[@itemprop="url"]/@href').get()
            item_loader.add_value('url', url)
            
            draft_item = item_loader.load_item()
            
            if self.content_controller.check_item(draft_item):
                print(f"----skipping item: {draft_item.name}")
                yield draft_item
                continue
            else:
                yield response.follow(url=url, callback=self.parse_item, cb_kwargs={'item': draft_item})


    def parse_item(self, response, item):
        print(f"----parsing item: {response.url}")
        
        loader = BaseLoader(item, response=response)

        loader.add_xpath('description', './/div[@class="gp-info"]//*[@itemprop="description"]/text()')

        loader.selector = response.css('.gp-more')
        loader.add_xpath('brand', './/*[@itemprop="brand"]/text()')
        loader.add_xpath('country', './li[3]/b/text()')
        loader.add_xpath('subtype', './li[4]/b/text()')

        separator = r"характе?ри?стик[аиуое]?|свойств[ао]?"
        loader.selector = response.css('.gp-descr').xpath(f'./*[re:test(., "{separator}", "i")]')
        if not loader.selector.get():
            loader.add_xpath('full_description', './/*[@class="gp-descr"]/p//text()')
        else:
            loader.add_xpath('full_description', 'preceding-sibling::p//text()')
            loader.add_xpath('additional_info', 'following-sibling::p//text()')

            if loader.selector.xpath('following-sibling::ul').get():
                loader.add_xpath('characteristics', 'following-sibling::ul/li//text()')
            else:
                loader.add_xpath('characteristics', './/text()')
        
        loader.add_value('update_status', "NEW")

        yield loader.load_item()



class GrainrusParser(Parser):

    def parse(self, response, item):
        loader = BaseLoader(item)
        loader.add_value('source_domain', 'grainrus')
        loader.add_value('currency', 'RUB')
        base_item = loader.load_item()

        yield from self.parse_page(response, base_item)

        pages = response.css('.modern-page-navigation > a::text').getall()
        try:
            last_page = int(pages[-2])
        except ValueError:
            last_page = 1

        if last_page > 1:
            pages_urls = [f"{response.url}?PAGEN_1={page}" for page in range(2, last_page + 1)]
            for page in pages_urls:
                yield response.follow(url=page, callback=self.parse_page, cb_kwargs={'item': base_item})

        
    def parse_page(self, response, item):
        product_cards = response.xpath('.//div[@class="productCardDescription 1"]')
        for card in product_cards:
            item_loader = BaseLoader(item=item.copy(), response=response, selector=card)

            item_loader.add_xpath('name', './a[1]/text()')
            item_loader.add_xpath('price', './*[last()]/div[@data-price]/@data-price')

            url = f"https://malt.ru{card.xpath('./a[1]/@href').get()}"
            item_loader.add_value('url', url)

            draft_item = item_loader.load_item()
            
            if self.content_controller.check_item(draft_item):
                print(f"----skipping item: {draft_item.name}")
                yield draft_item
                continue
            else:
                yield response.follow(url=url, callback=self.parse_item, cb_kwargs={'item': draft_item})


    def parse_item(self, response, item):
        print(f"----parsing item: {response.url}")
        
        loader = BaseLoader(item, response=response)

        loader.add_xpath('description', './/div[@class="description_prev_text"]/text()')

        loader.add_xpath('brand', './/*[@class="companyTitle"]/text()')
        loader.add_xpath('country', './/*[@class = "companyCountryText"]/text()')

        loader.add_xpath('full_description', './/section[@data-index="11"]/*[@class="information"]/p//text()')

        loader.add_xpath('characteristics', './/*[@class = "descriptionSpecificationItem"][1]/text()')
        
        yield loader.load_item()


class GrainrusHopsParser(GrainrusParser):
        
    def parse_page(self, response, item):
        product_cards = response.xpath('.//div[@class="productCardDescription 1"]')
        for card in product_cards:
            name = card.xpath('./a[1]/text()').get()
            url = f"https://malt.ru{card.xpath('./a[1]/@href').get()}"

            sel1 = card.xpath('./*[last()]/div[1]/div[@data-price]')
            
            options = [(s.xpath('./@data-price').get(), s.xpath('./p/text()').get()) for s in sel1]
            if not options:
                options = [(None, None)]
                
            for price, package in options:
                item_loader = BaseLoader(item = item.copy(), response = response, selector=card)
                
                adjusted_name = name
                if package:
                    adjusted_name = f"{name}, {package}"
                
                item_loader.add_value('name', adjusted_name)
                item_loader.add_value('price', price)

                item_loader.add_value('url', url)

                draft_item = item_loader.load_item()
                
                if self.content_controller.check_item(draft_item):
                    print(f"----skipping item: {draft_item.name}")
                    yield draft_item
                    continue
                else:
                    yield response.follow(url=url, callback=self.parse_item, cb_kwargs={'item': draft_item})


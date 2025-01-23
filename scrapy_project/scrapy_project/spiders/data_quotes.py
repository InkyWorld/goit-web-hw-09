import scrapy
from scrapy_project.scrapy_project.items import QuoteItem, AuthorItem
from scrapy_project.scrapy_project.pipelines import MongoPipeline
from scrapy.crawler import CrawlerProcess

class DataQuotesSpider(scrapy.Spider):
    name = "data_quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]
    custom_settings = {"ITEM_PIPELINES": {MongoPipeline: 300}}
    
    def parse(self, response, **kwargs):
        for q in response.xpath("/html//div[@class='quote']"):
            quote = q.xpath("span[@class='text']/text()").get().strip()
            author = q.xpath("span/small[@class='author']/text()").get().strip()
            tags = q.xpath("div[@class='tags']/a/text()").extract()
            # TODO: clear tags
            yield QuoteItem(quote=quote, author=author, tags=tags)
            yield response.follow(url=self.start_urls[0] + q.xpath("span/a/@href").get(), callback=self.parse_author)

        next_link = response.xpath("/html//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=self.start_urls[0] + next_link)

    @classmethod
    def parse_author(cls, response, **kwargs):
        content = response.xpath("/html//div[@class='author-details']")
        fullname = content.xpath("h3[@class='author-title']/text()").get().strip()
        born_date = content.xpath("p/span[@class='author-born-date']/text()").get().strip()
        born_location = content.xpath("p/span[@class='author-born-location']/text()").get().strip()
        description = content.xpath("div[@class='author-description']/text()").get().strip()
        yield AuthorItem(fullname=fullname, born_date=born_date, born_location=born_location, description=description)

import logging
from scrapy.utils.log import configure_logging
def run_spider():
    configure_logging(install_root_handler=False)

    # Suppress all logging output from Python's logging system
    logging.basicConfig(level=logging.CRITICAL)

    # Suppress Scrapy-specific loggers
    logging.getLogger('scrapy').setLevel(logging.CRITICAL)
    logging.getLogger('scrapy.utils.log').setLevel(logging.CRITICAL)
    logging.getLogger('scrapy.crawler').setLevel(logging.CRITICAL)
    logging.getLogger('scrapy.middleware').setLevel(logging.CRITICAL)
    logging.getLogger('scrapy.extensions').setLevel(logging.CRITICAL)

    # Suppress Twisted logs
    logging.getLogger('twisted').setLevel(logging.CRITICAL)

    # Suppress any additional noise during startup
    process = CrawlerProcess({
        'LOG_ENABLED': False,  # Disable Scrapy's internal logging
        'LOG_LEVEL': 'CRITICAL'  # Set log level to critical (if it tries to override)
    })
    # process = CrawlerProcess()
    process.crawl(DataQuotesSpider)
    process.start()

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json

from itemadapter import ItemAdapter

# class DataPipline:
#     quotes = []
#     authors = []

#     def process_item(self, item, spider):
#         adapter = ItemAdapter(item)
#         if 'fullname' in adapter.keys():
#             self.authors.append(dict(adapter))
#         if 'quote' in adapter.keys():
#             self.quotes.append(dict(adapter))

#     def close_spider(self, spider):
#         with open('quotes.json', 'w', encoding='utf-8') as fd:
#             json.dump(self.quotes, fd, ensure_ascii=False, indent=2)
#         with open('authors.json', 'w', encoding='utf-8') as fd:
#             json.dump(self.authors, fd, ensure_ascii=False, indent=2)

from mongoengine.errors import NotUniqueError
from models import Author, Quote
from scrapy_project.scrapy_project.items import AuthorItem, QuoteItem


class MongoPipeline:
    def process_item(self, item, spider):
        if isinstance(item, AuthorItem):
            # Check if the author already exists
            if not Author.objects(fullname=item.get("fullname")).first():
                obj = Author(
                    fullname=item.get("fullname"),
                    born_date=item.get("born_date"),
                    born_location=item.get("born_location"),
                    description=item.get("description"),
                )
                try:
                    obj.save()
                except NotUniqueError:
                    spider.logger.warning(f"Author '{obj.fullname}' already exists.")
                except Exception as e:
                    spider.logger.error(f"Failed to save author: {e}")

        if isinstance(item, QuoteItem):
            author_obj = Author.objects.get(fullname=item.get("author"))
            if not Quote.objects(
                    author=author_obj,
                    tags=item.get("tags"),
                    quote=item.get("quote"),
                ).first():
                obj = Quote(
                    author=author_obj,
                    tags=item.get("tags"),
                    quote=item.get("quote"),
                )
                try:
                    obj.save()
                except NotUniqueError:
                    spider.logger.warning(f"Quote '{obj.quote}' already exists.")
                except Exception as e:
                    spider.logger.error(f"Failed to save quote: {e}")
        return item

import json
from models import Author, Quote

from mongoengine.errors import NotUniqueError, DoesNotExist

import connection

def main():
    with open("data/authors.json", "r", encoding='utf-8') as fd:
        authors_data = json.load(fd)

    for item in authors_data:
        try:
            author_obj = Author(
                fullname=item.get("fullname"),
                born_date=item.get("born_date"),
                born_location=item.get("born_location"),
                description=item.get("description"),
            )
            author_obj.save()
        except NotUniqueError:
            print(f"Author '{item.get("fullname")}' already exists in the database.")

    with open("data/quotes.json", "r", encoding='utf-8') as fd:
        quotes_data = json.load(fd)

    for item in quotes_data:
        try:
            author_obj = Author.objects.get(fullname=item.get("author"))
            quote_obj = Quote(
                author=author_obj,
                quote=item.get("quote"),
                tags=item.get("tags"),
            )
            quote_obj.save()
        except DoesNotExist:
            print(f"Author '{item.get('author')}' not found for quote: {item.get('quote')}")

if __name__ == "__main__":
    main()

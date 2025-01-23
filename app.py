import json
import redis
from redis_lru import RedisLRU
from models import Author, Quote

from mongoengine.queryset import QuerySet
from mongoengine.errors import NotUniqueError, DoesNotExist

from scrapy_project.scrapy_project.spiders.data_quotes import run_spider
import connection

# Підключення до Redis
client = redis.StrictRedis(host="localhost", port=6379, password=None)
cache = RedisLRU(client)


@cache
def find_by_tag(tag: str) -> list[str]:
    print(f"Find by {tag}")
    quotes = Quote.objects(tags__iregex=tag)
    return set(q.quote for q in quotes)


@cache
def find_by_author(author: str) -> list[str]:
    print(f"Find by author: {author}")
    authors = Author.objects(fullname__iregex=author)
    result = []
    for a in authors:
        result.extend([q.quote for q in Quote.objects(author=a)])
    return result

@cache
def find_by_tags(tags: list[str]) -> set[str]:
    print(f"Find by {tags}")
    quotes = []
    for tag in tags:
        quotes.extend(Quote.objects(tags__iregex=tag))
    return set(q.quote for q in quotes)


def main():
    while True:
        user_input = input("Введіть команду (наприклад, name: Steve Martin, tag:life, tags:life,live): ").strip()

        if user_input.lower() == "exit":
            print("Завершення роботи.")
            break

        if user_input.startswith("name:"):
            author_name = user_input[len("name:"):].strip()
            quotes = find_by_author(author_name)
            print("Цитати автора:", author_name)
            print("\n".join(quotes))

        elif user_input.startswith("tag:"):
            tag_name = user_input[len("tag:"):].strip()
            quotes = find_by_tag(tag_name)
            print(f"Цитати для тегу: {tag_name}")
            print("\n".join(quotes))

        elif user_input.startswith("tags:"):
            tags_str = user_input[len("tags:"):].strip()
            tags = tags_str.split(",")
            quotes = find_by_tags(tags)
            print(f"Цитати для тегів: {', '.join(tags)}")
            print("\n".join(quotes))

        elif user_input.startswith("reload_db"):
            run_spider()
            print("json reloaded")

        else:
            print("Невірна команда, спробуйте знову.")


if __name__ == "__main__":
    main()

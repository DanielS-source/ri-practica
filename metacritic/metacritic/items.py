# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MetacriticItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    url = scrapy.Field()
    summary = scrapy.Field()
    genre = scrapy.Field()
    metascore = scrapy.Field()
    critic_reviews = scrapy.Field()
    user_score = scrapy.Field()
    user_reviews = scrapy.Field()
    release_date = scrapy.Field()
    producer = scrapy.Field()

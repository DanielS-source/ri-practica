# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MetacriticItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    title_search = scrapy.Field()  # For searching purposes
    title_keyword = scrapy.Field() # For ordering purposes
    url = scrapy.Field()
    summary = scrapy.Field()
    genre = scrapy.Field()
    metascore = scrapy.Field()
    critic_reviews = scrapy.Field()
    user_score = scrapy.Field()
    user_reviews = scrapy.Field()
    release_date = scrapy.Field()
    images = scrapy.Field()
    video = scrapy.Field()
    video_type = scrapy.Field()
    sentiment = scrapy.Field()
    must_play = scrapy.Field()
    crew = scrapy.Field()
    countries = scrapy.Field()
    companies = scrapy.Field()
    platforms = scrapy.Field()
    rating = scrapy.Field()
    official_site = scrapy.Field()

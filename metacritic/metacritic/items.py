# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import json
from scrapy.item import Item, Field

class MetacriticItem(Item):
    # define the fields for your item here like:
    title = Field()
    title_search = Field()  # For searching purposes
    title_keyword = Field() # For ordering purposes
    url = Field()
    summary = Field()
    genre = Field()
    metascore = Field()
    critic_reviews = Field()
    user_score = Field()
    user_reviews = Field()
    release_date = Field()
    images = Field()
    video = Field()
    video_thumbnail = Field()
    video_type = Field()
    sentiment = Field()
    must_play = Field()
    crew = Field()
    countries = Field()
    companies = Field()
    platforms = Field()
    rating = Field()



class MetacriticItemEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MetacriticItem):
            return {
                'title': (obj["title"] if "title" in obj else None),   
                'title_search': (obj["title_search"] if "title_search" in obj else None),  
                'title_keyword': (obj["title_keyword"] if "title_keyword" in obj else None),  
                'url': (obj["url"] if "url" in obj else None), 
                'summary': (obj["summary"] if "summary" in obj else None), 
                'genre': (obj["genre"] if "genre" in obj else None), 
                'metascore': (obj["metascore"] if "metascore" in obj else 0), 
                'critic_reviews': (obj["critic_reviews"] if "critic_reviews" in obj else 0),  
                'user_score': (obj["user_score"] if "user_reviews" in obj else None), 
                'user_reviews': (obj["user_reviews"] if "user_reviews" in obj else 0), 
                'release_date': (obj["release_date"] if "release_date" in obj else None), 
                'images': (obj["images"] if "images" in obj else []), 
                'video': (obj["video"] if "video" in obj else ""), 
                'video_thumbnail': (obj["video_thumbnail"] if "video_thumbnail" in obj else ""), 
                'video_type': (obj["video_type"] if "video_type" in obj else None),
                'sentiment': (obj["sentiment"] if "sentiment" in obj else None), 
                'must_play': (obj["must_play"] if "must_play" in obj else None),
                'crew': (obj["crew"] if "crew" in obj else []),
                'countries': (obj["countries"] if "countries" in obj else []), 
                'companies': (obj["companies"] if "companies" in obj else []),  
                'platforms': (obj["platforms"] if "platforms" in obj else []),   
                'rating': (obj["rating"] if "rating" in obj else None)
            }
            return {}
        return super().default(obj)
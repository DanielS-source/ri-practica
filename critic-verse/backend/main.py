import re
from typing import Union
from fastapi import APIRouter, Body, Depends, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import uvicorn
from elasticsearch import Elasticsearch
import datetime
from pydantic import BaseModel

load_dotenv()

ELASTIC_SCHEME = os.getenv("ELASTIC_SCHEME", default="http")
ELASTIC_HOST = os.getenv("ELASTIC_HOST", default="localhost")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", default=9200))
BACKEND_HOST = os.getenv("BACKEND_HOST", default="localhost")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", default=8000))
ROOT_PATH = os.getenv("ROOT_PATH", default="/api/v1")
PAGE_SIZE = int(os.getenv("PAGE_SIZE", default=50))

INDEX = os.getenv("INDEX", default="metacritic")

es = Elasticsearch([{'scheme': ELASTIC_SCHEME, 'host': ELASTIC_HOST, 'port': ELASTIC_PORT}])

app = FastAPI()
origins = ["*"]
methods = ["*"]
headers = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=headers,
)

class MetacriticItem(BaseModel):
    title: str | None = None
    title_asc: bool | None = None
    genre: str | None = None
    platform: str | None = None
    country: str | None = None
    metascore_min: int | None = None
    metascore_max: int | None = None
    critic_reviews_min: int | None = None
    critic_reviews_max: int | None = None
    metascore_asc: bool | None = None
    user_score_min: int | None = None
    user_score_max: int | None = None
    user_reviews_min: int | None = None
    user_reviews_max: int | None = None
    user_score_asc: bool | None = None
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    date_asc: bool | None = None
    page: int | None = 0
    size: int | None = PAGE_SIZE

# Transforms the string removing special characters, leaving only letters, numbers and spaces.
def normalize_string(input_string):    
    return re.sub(r'[^a-zA-Z0-9\s]', '', input_string)

def parse_data(response):
    server_response = {
        "time": response["took"],
        "n_hits": response["hits"]["total"]["value"],
        #"relation": response["hits"]["total"]["relation"],
        "hits": response["hits"]["hits"]
    }
    return JSONResponse(content=server_response)

@app.get(ROOT_PATH + "/")
def get_all_results(
    page: int = Query(0, description="Page", ),
    size: int = Query(PAGE_SIZE, description="Size", ),
):
    query = {
        "size": PAGE_SIZE,
        "from": 0,
        "query": {
            "match_all": {}  
        }
    }
    if(size < PAGE_SIZE):
        query["size"] = PAGE_SIZE
    response = es.search(index=INDEX, body=query)
    return parse_data(response)

@app.post(ROOT_PATH + "/search")
def multisearch(
    item: MetacriticItem
):
    sorts = []
    # Query template
    query = {
        "size": int(item.size),
        "from": int(item.page),
        "query": {"bool": {"must": [], "should": []}},  
        "sort": []
    }
    range = 0
    if(item.size < PAGE_SIZE):
        query["size"] = PAGE_SIZE
    if(item.title != None and len(item.title) > 0):
        query["query"]["bool"]["must"].append({"match": {"title_search": normalize_string(item.title)}})
    if(item.title_asc != None):
        sorts.append({"title_keyword": ("asc" if item.title_asc else "desc")})
    if(item.genre != None):
        genres = item.genre.split(", ")
        for g in genres:
            query["query"]["bool"]["should"].append({"match": {"genre": g}})
    if(item.platform != None):
        platforms = item.platform.split(", ")
        for p in platforms:
            query["query"]["bool"]["must"].append({"match": {"platforms": p}})
    if(item.country != None):
        countries = item.country.split(", ")
        for c in countries:
            query["query"]["bool"]["must"].append({"match": {"countries": c}})
    if(item.metascore_min != None):
        if(item.metascore_max != None and int(item.metascore_max) >= int(item.metascore_min)):
            query["query"]["bool"]["must"].append({"range": { "metascore": {
                "gte": int(item.metascore_min),
                "lte": int(item.metascore_max)
            }}})
        else:
            query["query"]["bool"]["must"].append({"range": { "metascore": { "gte": int(item.metascore_min) } } })

    if(item.critic_reviews_min != None):
        if(item.critic_reviews_max != None and int(item.critic_reviews_max) >= int(item.critic_reviews_min)):
            query["query"]["bool"]["must"].append({"range": { "critic_reviews": {
                "gte": int(item.critic_reviews_min),
                "lte": int(item.critic_reviews_max)
            }}})
        else:
            query["query"]["bool"]["must"].append({"range": { "critic_reviews": { "gte": int(item.critic_reviews_min) } } })

    if(item.metascore_asc != None):
        sorts.append({"metascore": ("asc" if item.metascore_asc else "desc")})
    if(item.user_score_min != None):
        if(item.user_score_max!= None and int(item.user_score_max) >= int(item.user_score_min)):
            query["query"]["bool"]["must"].append({"range": { "user_score": {
                "gte": int(item.user_score_min),
                "lte": int(item.user_score_max)
            }}})
        else:
            query["query"]["bool"]["must"].append({"range": { "user_score": { "gte": int(item.user_score_min) } } })

    if(item.user_reviews_min != None):
        if(item.user_reviews_max!= None and int(item.user_reviews_max) >= int(item.user_reviews_min)):
            query["query"]["bool"]["must"].append({"range": { "user_reviews": {
                "gte": int(item.user_reviews_min),
                "lte": int(item.user_reviews_max)
            }}})
        else:
            query["query"]["bool"]["must"].append({"range": { "user_reviews": { "gte": int(item.user_reviews_min) } } })
    
    if(item.user_score_asc!= None):
        sorts.append({"user_score": ("asc" if item.user_score_asc else "desc")})

    if(item.start_date!= None):
        if(item.end_date != None and item.start_date <= item.end_date):
            query["query"]["bool"]["should"].append({"bool": {"must_not": {"exists": {"field": "release_date"}}}})
            query["query"]["bool"]["should"].append({"range": { "release_date": {
                "gte": item.start_date.strftime("%Y-%m-%d"),
                "lte": item.end_date.strftime("%Y-%m-%d")
            }}})
        else:
            query["query"]["bool"]["should"].append({"bool": {"must_not": {"exists": {"field": "release_date"}}}})
            query["query"]["bool"]["should"].append({"range": { "release_date": {
                "gte": item.start_date.strftime("%Y-%m-%d")
            }}})
    if(item.date_asc!= None):
        sorts.append({"release_date": ("asc" if item.date_asc else "desc")})

    query["sort"] = sorts
    if(query["query"] == {}):
        query["query"] = {"match_all": {}}
    response = es.search(index=INDEX, body=query)
    return parse_data(response)


@app.get(ROOT_PATH + "/user-reviews")
def get_user_reviews(
    max: bool = Query(None, description="Get the max/min user reviews (True = Maximum | False = Minimum)", ),
):
    query = { 
        "size": 0,
        "aggs": {}
    }  
    if max:
        query["aggs"] = {"max_user_reviews": {"max": {"field": "user_reviews"}}}
    else:
        query["aggs"] = {"min_user_reviews": {"min": {"field": "user_reviews"}}}
        
    response = es.search(index=INDEX, body=query)
    if "aggregations" in response:
        return (response["aggregations"]["max_user_reviews"]["value"] if max 
                else response["aggregations"]["min_user_reviews"]["value"])
    return response

@app.get(ROOT_PATH + "/critic-reviews")
def get_critic_reviews(
    max: bool = Query(None, description="Get the max/min critic reviews (True = Maximum | False = Minimum)", ),
):
    query = { 
        "size": 0,
        "aggs": {}
    }  
    if max:
        query["aggs"] = {"max_critic_reviews": {"max": {"field": "critic_reviews"}}}
    else:
        query["aggs"] = {"min_critic_reviews": {"min": {"field": "critic_reviews"}}}
        
    response = es.search(index=INDEX, body=query)
    if "aggregations" in response:
        return (response["aggregations"]["max_critic_reviews"]["value"] if max 
                else response["aggregations"]["min_critic_reviews"]["value"])
    return response

@app.get(ROOT_PATH + "/genres")
def get_genres():
    query = { 
        "size": 0,
        "aggs": {}
    }  
    query["aggs"] = {"unique_genres": {"terms": {"field": 'genre'}}}
        
    response = es.search(index=INDEX, body=query)

    genre_list = []
    if "aggregations" in response:
        for genre in response["aggregations"]["unique_genres"]["buckets"]:
            genre_list.append(genre["key"])
        return genre_list
    return genre_list

@app.get(ROOT_PATH + "/platforms")
def get_platforms():
    query = { 
        "size": 0,
        "aggs": {}
    }  
    query["aggs"] = {"unique_platforms": {"terms": {"field": 'platforms'}}}
        
    response = es.search(index=INDEX, body=query)

    platform_list = []
    if "aggregations" in response:
        for platform in response["aggregations"]["unique_platforms"]["buckets"]:
            platform_list.append(platform["key"])
        return platform_list
    return platform_list

@app.get(ROOT_PATH + "/countries")
def get_countries():
    query = { 
        "size": 0,
        "aggs": {}
    }  
    query["aggs"] = {"unique_countries": {"terms": {"field": 'countries'}}}
        
    response = es.search(index=INDEX, body=query)

    country_list = []
    if "aggregations" in response:
        for country in response["aggregations"]["unique_countries"]["buckets"]:
            country_list.append(country["key"])
        return country_list
    return country_list

@app.get(ROOT_PATH + "/titles")
def search_by_title(
    q: str = Query(None, description="Title", ),
):
    if q:
        query = {
            "query": {
                "match_phrase_prefix": {
                    "title": q
                }
            }
        }
        response = es.search(index=INDEX, body=query)
        return parse_data(response)
    else:
        return {"detail":"Not Found"}
        
@app.get(ROOT_PATH + "/genres")
def search_by_genre(
    q: str = Query(None, description="Genre", ),
):
    if q:
        query = {
            "query": {
                "match": {
                    "genre": q
                }
            }
        }
        response = es.search(index=INDEX, body=query)
        return parse_data(response)
    else:
        return {"detail":"Not Found"}

@app.get(ROOT_PATH + "/metascore")
def search_by_metascore(
    metascore: int = Query(None, description="Metascore", ),
):
    if metascore:
        query = {
            "query": {
                "range": {
                    "metascore": {
                        "gte": metascore
                    }
                }
            }
        }
        response = es.search(index=INDEX, body=query)
        return parse_data(response)
    else:
        return {"detail":"Not Found"}
        
@app.get(ROOT_PATH + "/user_score")
def search_by_user_score(
    q: str = Query(None, description="User score", ),
):
    if q:
        query = {
            "query": {
                "match_all": {}
            },
            "sort": [
                { "user_score": "desc" }
            ]
        }
        response = es.search(index=INDEX, body=query)
        return parse_data(response)
    else:
        return {"detail":"Not Found"}
    
@app.get(ROOT_PATH + "/date_range")
def search_by_date_range(   
    start_date: datetime.date = datetime.date.today(),
    end_date: datetime.date = None
):
        
    query = {
        "query": {
            "range": {
                "release_date": {
                    "gte": start_date
                }
            }
        }
    }
    
    if end_date is not None:
        query["query"]["range"]["release_date"]["lte"] = end_date.strftime("%Y-%m-%d")
        
    response = es.search(index=INDEX, body=query)
    return parse_data(response)

if __name__ == "__main__":
    uvicorn_config = {
        "app": "main:app",
        "host": BACKEND_HOST,
        "port": BACKEND_PORT
    }
    uvicorn.run(**uvicorn_config)
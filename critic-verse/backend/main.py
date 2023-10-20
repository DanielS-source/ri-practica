from typing import Union
from fastapi import APIRouter, Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import uvicorn
from elasticsearch import Elasticsearch
import datetime

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

def parse_data(response):
    server_response = {
        "time": response["took"],
        "n_hits": response["hits"]["total"]["value"],
        #"relation": response["hits"]["total"]["relation"],
        "hits": response["hits"]["hits"]
    }
    return JSONResponse(content=server_response)

@app.get(ROOT_PATH + "/")
def get_all_results():
    query = {
        "query": {
            "match_all": {}  
        }
    }
    response = es.search(index=INDEX, body=query)
    return parse_data(response)

@app.get(ROOT_PATH + "/search")
def multisearch(
    title: str = Query(None, description="Title", ),
    title_asc: bool = Query(None, description="Title asc (True) / desc (False)", ),
    genre: str = Query(None, description="Genre (Use commas for multiples genres)", ),
    platform: str = Query(None, description="Platforms (Use commas for multiples platforms)", ),
    country: str = Query(None, description="Countries (Use commas for multiples countries)", ),
    metascore_min: int = Query(None, description="Metascore min", ),
    metascore_max: int = Query(None, description="Metascore max", ),
    critic_reviews_min: int = Query(None, description="Metascore reviews min", ),
    critic_reviews_max: int = Query(None, description="Metascore reviews max", ),
    metascore_asc: bool = Query(None, description="Metascore asc (True) / desc (False)", ),
    user_score_min: int = Query(None, description="User score min", ),
    user_score_max: int = Query(None, description="User score max", ),
    user_reviews_min: int = Query(None, description="User reviews min", ),
    user_reviews_max: int = Query(None, description="User reviews max", ),
    user_score_asc: bool = Query(None, description="User score asc (True) / desc (False)", ),
    start_date: datetime.date = Query(None, description="Start date", ),
    end_date: datetime.date = Query(None, description="End date", ),
    date_asc: bool = Query(None, description="Date asc (True) / desc (False)", ),
    page: int = Query(0, description="Page", ),
    size: int = Query(PAGE_SIZE, description="Size", ),
):
    sorts = []
    # Query template
    query = {
        "size": int(size),
        "from": int(page),
        "query": {},  
        "sort": []
    }
    range = 0
    if(size < PAGE_SIZE):
        query["size"] = PAGE_SIZE
    if(title != None):
        query["query"]["match_phrase_prefix"] = {"title": title}
    if(title_asc != None):
        sorts.append({"title", "asc" if title_asc else "desc"})
    if(genre != None):
        if("bool" not in query["query"]):
            query["query"]["bool"] = {"must": []}
        genres = genre.split(", ")
        query["query"]["bool"] = {"must": []}
        for g in genres:
            query["query"]["bool"]["must"].append({"match": {"genre": g}})
    if(platform != None):
        if("bool" not in query["query"]):
            query["query"]["bool"] = {"must": []}
        platforms = platform.split(", ")
        for p in platforms:
            query["query"]["bool"]["must"].append({"match": {"platforms": p}})
    if(country != None):
        if("bool" not in query["query"]):
            query["query"]["bool"] = {"must": []}
        countries = country.split(", ")
        for c in countries:
            query["query"]["bool"]["must"].append({"match": {"countries": c}})
    if(metascore_min != None):
        if("bool" not in query["query"]):
            query["query"]["bool"] = {"must": []}
        if(metascore_max != None and int(metascore_max) >= int(metascore_min)):
            query["query"]["bool"]["must"].append({"range": { "metascore": {
                "gte": int(metascore_min),
                "lte": int(metascore_max)
            }}})
        else:
            query["query"]["bool"]["must"].append({"range": { "metascore": { "gte": int(metascore_min) } } })

    if(critic_reviews_min != None):
        if("bool" not in query["query"]):
            query["query"]["bool"] = {"must": []}
        if(critic_reviews_max != None and int(critic_reviews_max) >= int(critic_reviews_min)):
            query["query"]["bool"]["must"].append({"range": { "critic_reviews": {
                "gte": int(critic_reviews_min),
                "lte": int(critic_reviews_max)
            }}})
        else:
            query["query"]["bool"]["must"].append({"range": { "critic_reviews": { "gte": int(critic_reviews_min) } } })

    if(metascore_asc != None):
        sorts.append({"metascore", "asc" if metascore_asc else "desc"})
    if(user_score_min != None):
        if("bool" not in query["query"]):
            query["query"]["bool"] = {"must": []}
        if(user_score_max!= None and int(user_score_max) >= int(user_score_min)):
            query["query"]["bool"]["must"].append({"range": { "user_score": {
                "gte": int(user_score_min),
                "lte": int(user_score_max)
            }}})
        else:
            query["query"]["bool"]["must"].append({"range": { "user_score": { "gte": int(user_score_min) } } })

    if(user_reviews_min != None):
        if("bool" not in query["query"]):
            query["query"]["bool"] = {"must": []}
        if(user_reviews_max!= None and int(user_reviews_max) >= int(user_reviews_min)):
            query["query"]["bool"]["must"].append({"range": { "user_reviews": {
                "gte": int(user_reviews_min),
                "lte": int(user_reviews_max)
            }}})
        else:
            query["query"]["bool"]["must"].append({"range": { "user_reviews": { "gte": int(user_reviews_min) } } })
    
    if(user_score_asc!= None):
        sorts.append({"user_score", "asc" if user_score_asc else "desc"})

    if(start_date!= None):
        if("bool" not in query["query"]):
            query["query"]["bool"] = {"must": []}
        if(end_date != None and start_date <= end_date):
            query["query"]["bool"]["must"].append({"range": { "release_date": {
                "gte": start_date.strftime("%Y-%m-%d"),
                "lte": end_date.strftime("%Y-%m-%d")
            }}})
        else:
            query["query"]["bool"]["must"].append({"range": { "release_date": {
                "gte": start_date.strftime("%Y-%m-%d")
            }}})
    if(date_asc!= None):
        sorts.append({"date_asc", "asc" if date_asc else "desc"})

    query["sort"] = sorts
    if(query["query"] == {}):
        query["query"] = {"match_all": {}}
    print("\n")
    print(query)
    print("\n")
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
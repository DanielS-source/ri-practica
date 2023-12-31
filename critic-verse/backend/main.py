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
from unidecode import unidecode

load_dotenv()

ELASTIC_SCHEME = os.getenv("ELASTIC_SCHEME", default="http")
ELASTIC_HOST = os.getenv("ELASTIC_HOST", default="localhost")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", default=9200))
BACKEND_HOST = os.getenv("BACKEND_HOST", default="localhost")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", default=8000))
ROOT_PATH = os.getenv("ROOT_PATH", default="/api/v1")
PAGE_SIZE = int(os.getenv("PAGE_SIZE", default=12))
MAX_SUGGESTIONS = int(os.getenv("MAX_SUGGESTIONS", default=8))
MAX_ALTERNATIVES = int(os.getenv("MAX_ALTERNATIVES", default=8))
MAX_RELEVANCE_DOCS = int(os.getenv("MAX_RELEVANCE_DOCS", default=100))

INDEX = os.getenv("INDEX", default="metacritic")

es = Elasticsearch([{'scheme': ELASTIC_SCHEME, 'host': ELASTIC_HOST, 'port': ELASTIC_PORT}])

relevant_docs = []

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
    critic_score_min: int | None = None
    critic_score_max: int | None = None
    #critic_reviews_min: int | None = None
    #critic_reviews_max: int | None = None
    user_score_min: int | None = None
    user_score_max: int | None = None
    #user_reviews_min: int | None = None
    #user_reviews_max: int | None = None
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    sort_by: str | None = None
    sort_direction: str | None = None
    page: int | None = 0
    size: int | None = PAGE_SIZE

# Transforms the string removing special characters, leaving only letters, numbers and spaces.
def normalize_string(input_string):    
    return re.sub(r'[^a-zA-Z0-9\s]', '', unidecode(input_string))

def normalize_string_lower(input_string):    
    return re.sub(r'[^a-zA-Z0-9\s]', '', unidecode(input_string)).replace('  ', ' ').lower().strip()

# Custom implementation for completion suggester highlighting
def highlight_word(word, input_string):
    data = normalize_string_lower(input_string['_source']['title_search'])
    word_normalized = normalize_string_lower(word)
    fpos = data.find(word_normalized)
    if(fpos > -1):
        word_len = (fpos + len(word_normalized))
        input_string['_source']['title_search'] = input_string['_source']['title_search'][0:fpos] + \
                                            "<b>"+input_string['_source']['title_search'][fpos:word_len] + "</b>" + \
                                            input_string['_source']['title_search'][word_len:]
    return input_string

def highlight_array(word, array):
    return [highlight_word(word, input_string) for input_string in array]

def parse_data(response, page, size):
    server_response = {
        "time": (int(response["took"])/1000 if "took" in response else -1), # Seconds
        "size": int(size),
        "page": int(page), 
        "n_pages": (round(int(response["hits"]["total"]["value"])/(size), 0) if "hits" in response else -1),
        "n_hits": (response["hits"]["total"]["value"] if "hits" in response else -1), # Number of hits
        #"relation": response["hits"]["total"]["relation"],
        "hits": (response["hits"]["hits"] if "hits" in response else -1)
    }
    return JSONResponse(content=server_response) 

def parse_data_suggestions(word, response, alts):
    server_response = {
        "time": (int(response["took"])/1000 if "took" in response else -1), # Seconds
        "alt": bool(alts),
        "hits": (response["hits"]["hits"] if "hits" in response else []),
        "suggestions": (highlight_array(word, response["suggest"]["game-suggest"][0]["options"]) if "suggest" in response else [])
    }
    return JSONResponse(content=server_response)   

@app.get(ROOT_PATH + "/")
def get_all_results(
    page: int = Query(0, description="Page", ),
    size: int = Query(PAGE_SIZE, description="Size", ),
):
    query = {
        "size": PAGE_SIZE,
        "from": int(size * page),
        "query": {
            "match_all": {}  
        }
    }
    if(size < PAGE_SIZE):
        query["size"] = PAGE_SIZE
    query["from"] = int(size*page)
    response = es.search(index=INDEX, body=query)
    return parse_data(response, 0, PAGE_SIZE)

@app.post(ROOT_PATH + "/search")
def multisearch(
    item: MetacriticItem
):
    sorts = []
    # Query template
    query = {
        "size": int(item.size),
        "from": int(item.page*item.size),
        "query": {
            "bool": {
                "must": [], 
                "should": []
            }
        },  
        "sort": [],
        "collapse": {
            "field": "title_keyword"  # Don't show duplicated hits with this field
        }
    }
    
    # Relevance feedback
    if (len(relevant_docs) > 0):
        query["query"]["bool"]["should"].append({"more_like_this": {"fields": ["title_search"], "like": relevant_docs, "min_term_freq": 1, "min_doc_freq": 1}})

    range = 0
    if(item.size < PAGE_SIZE):
        query["size"] = PAGE_SIZE
    if(item.title != None and len(item.title) > 0):
        query["query"]["bool"]["must"].append({"match": {"title_search": normalize_string(item.title)}})
        query["query"]["bool"]["should"].append({"wildcard": {"summary": "*"+normalize_string(item.title)+"*"}})

    # Sorting
    
    if (item.sort_by != None):
        sorting = "asc" if item.sort_direction == "Ascending" else "desc"
        if (item.sort_by == "title"):
            sorts.append({"title_keyword": sorting})
        if (item.sort_by == "critic_score"):
            sorts.append({"metascore": sorting})
        if (item.sort_by == "user_score"):
            sorts.append({"user_score": sorting})
        if (item.sort_by == "release_date"):
            sorts.append({"release_date": sorting})

    if(item.genre != None):
        genres = item.genre.split(", ")
        for g in genres:
            query["query"]["bool"]["should"].append({"match": {"genre": g}})
    if(item.platform != None):
        platforms = item.platform.split(", ")
        for p in platforms:
            query["query"]["bool"]["must"].append({"match": {"platforms": p}})

    if(item.country != None):
        query["query"]["bool"]["should"].append({"match": {"countries": item.country}})

    if(item.critic_score_min != None):
        if(item.critic_score_max != None and int(item.critic_score_max) >= int(item.critic_score_min)):
            query["query"]["bool"]["must"].append({"range": { "metascore": {
                "gte": int(item.critic_score_min),
                "lte": int(item.critic_score_max)
            }}})
        else:
            query["query"]["bool"]["must"].append({"range": { "metascore": { "gte": int(item.critic_score_min) } } })
    
    if(item.user_score_min != None):
        if(item.user_score_max!= None and int(item.user_score_max) >= int(item.user_score_min)):
            query["query"]["bool"]["must"].append({"range": { "user_score": {
                "gte": int(item.user_score_min),
                "lte": int(item.user_score_max)
            }}})
        else:
            query["query"]["bool"]["must"].append({"range": { "user_score": { "gte": int(item.user_score_min) } } })

    if(item.start_date!= None):
        d_start = item.start_date.strftime("%Y-%m-%d")
        if (item.end_date!= None):
            d_end = item.end_date.strftime("%Y-%m-%d")

            if(d_start == d_end):
                query["query"]["bool"]["should"].append({"bool": {"must_not": {"exists": {"field": "release_date"}}}})
                query["query"]["bool"]["must"].append({"match": { "release_date": item.start_date.strftime("%Y-%m-%d")}})

            elif(item.end_date != None and d_start <= d_end):
                query["query"]["bool"]["should"].append({"bool": {"must_not": {"exists": {"field": "release_date"}}}})
                query["query"]["bool"]["must"].append({"range": { "release_date": {
                    "gte": item.start_date.strftime("%Y-%m-%d"),
                    "lte": item.end_date.strftime("%Y-%m-%d")
                }}})
        else:
            query["query"]["bool"]["should"].append({"bool": {"must_not": {"exists": {"field": "release_date"}}}})
            query["query"]["bool"]["must"].append({"range": { "release_date": {
                "gte": item.start_date.strftime("%Y-%m-%d")
            }}})


    query["sort"] = sorts
    if(query["query"] == {}):
        query["query"] = {"match_all": {}}
    response = es.search(index=INDEX, body=query)
    return parse_data(response, item.page, item.size)


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
    query["aggs"] = {"unique_genres": {"terms": {"field": 'genre', "order": { "_key": "asc" }, "size": 200}}}
        
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
    query["aggs"] = {"unique_platforms": {"terms": {"field": 'platforms', "order": { "_key": "asc" }, "size": 50}}}
        
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
    query["aggs"] = {"unique_countries": {"terms": {"field": 'countries', "size": 50}}}
        
    response = es.search(index=INDEX, body=query)

    country_list = []
    if "aggregations" in response:
        for country in response["aggregations"]["unique_countries"]["buckets"]:
            country_list.append(country["key"])
        return country_list
    return country_list

# Relevance feedback

@app.post(ROOT_PATH + "/relevance/add")
def add_relevance(title: str = Body(..., description="Title", examples=["mario kart ds"], embed=True)):
    if title and len(title) > 0 and title not in relevant_docs:
        if(len(relevant_docs) >= MAX_RELEVANCE_DOCS):
            relevant_docs.pop(0)                        # Delete first doc
        relevant_docs.append(title)
    return {}

@app.post(ROOT_PATH + "/relevance/delete")
def delete_relevance(title: str = Body(..., description="Title", examples=["mario kart ds"], embed=True)):
    if title and len(title) > 0 and title in relevant_docs:
        relevant_docs.remove(title)
    return {}


@app.post(ROOT_PATH + "/suggestions")
def get_suggestions(
    title: str = Body(..., description="Title", examples=["Pokém"], embed=True),
):
    alternatives = False
    if title and len(title) > 0:
        query = {
            "_source": ["title_search"],                # Return the title search only
            "suggest": {
                "game-suggest": {
                    "prefix": normalize_string(title),
                    "completion": {
                        "field": "title_search.suggest",
                        "size": MAX_SUGGESTIONS,
                        "skip_duplicates": True         # Don't show duplicates in suggestions
                    }
                }
            },
            "sort": [{
                "_score": "desc"
            }, {
                "user_score": "desc"
            }],
            # Not working with completion suggester! (Known bug in Elasticsearch)
            #
            #"highlight": {
            #    "fields": [{"title_search": {}}]
            #}
        }

        alternatives_query = {
            "from": 0,
            "size": MAX_ALTERNATIVES,                   # Max alternatives per query
            "_source": ["title_search"],                # Return the title search only
            "query": {
                "bool": {
                    "must": [ 
                    {
                        "match": {
                            "title_search": normalize_string(title)
                        }
                    }],
                    "should": [{
                        "wildcard": {
                            "summary": "*"+normalize_string(title)+"*"
                        }
                    }]
                }               
            },
            "highlight": {
                "pre_tags":["<b>"], 
                "post_tags": ["</b>"],
                "fields": [{"title_search": {}}]
            },
            "sort": [{
                "_score": "desc"
            }, {
                "user_score": "desc"
            }], 
            "collapse": {
                "field": "title_keyword"                # Don't show duplicated hits with this field
            }
        }

        # Relevance feedback
        if (len(relevant_docs) > 0):
            alternatives_query["query"]["bool"]["should"].append({"more_like_this": {"fields": ["title_search"], "like": relevant_docs, "min_term_freq": 1, "min_doc_freq": 1}})

        response = es.search(index=INDEX, body=query)

        # If no suggestions then load alternatives
        if(len(response["suggest"]["game-suggest"][0]["options"]) == 0):
            alternatives = True
            response = es.search(index=INDEX, body=alternatives_query)
                    
        return parse_data_suggestions(title, response, alternatives)
    else:
        return parse_data_suggestions(title, {}, alternatives)
    
@app.get(ROOT_PATH + "/title/search")
def search_by_title(
    title: str = Query(None, description="Title or description"),
):
    if title:
        query = {
            "query": {
                "bool": {
                    "must": [], 
                    "should": []
                }
            }
        }
        query["query"]["bool"]["must"].append({"match": {"title_search": normalize_string(title)}})
        query["query"]["bool"]["should"].append({"wildcard": {"summary": "*"+normalize_string(title)+"*"}})
        response = es.search(index=INDEX, body=query)
        return parse_data(response, 0, PAGE_SIZE)
    else:
        return {"detail":"Not Found"}
        
@app.get(ROOT_PATH + "/genres/search")
def search_by_genre(
    genre: str = Query(None, description="Genre"),
):
    if genre:
        query = {
            "query": {
                "match": {}
            }
        }
        query["query"]["match"]["genre"] = {"genre": genre}
        response = es.search(index=INDEX, body=query)
        return parse_data(response, 0, PAGE_SIZE)
    else:
        return {"detail":"Not Found"}

@app.get(ROOT_PATH + "/critic-score/search")
def search_by_metascore(
    critic_score: int = Query(None, description="Search for games with critic score less than equal your value."),
):
    if critic_score:
        query = {
            "query": {
                "range": {
                    "metascore": {}
                }
            }
        }
        query["query"]["range"]["metascore"] = {"lte": critic_score}
        response = es.search(index=INDEX, body=query)
        return parse_data(response, 0, PAGE_SIZE)
    else:
        return {"detail":"Not Found"}
        
@app.get(ROOT_PATH + "/user_score/search")
def search_by_user_score(
    user_score: str = Query(None, description="Search for games with user score less than equal your value."),
):
    if user_score:
        query = {
            "query": {
                "range": {
                    "user_score": {}
                }
            }
        }
        query["query"]["range"]["user_score"] = {"lte": user_score}
        query["sort"].append({"user_score":"desc"})
        response = es.search(index=INDEX, body=query)
        return parse_data(response, 0, PAGE_SIZE)
    else:
        return {"detail":"Not Found"}
    
@app.get(ROOT_PATH + "/date_range/search")
def search_by_date_range(   
    start_date: datetime.date = datetime.date.today(),
    end_date: datetime.date = None
):
        
    query = {
        "query": {
            "range": {
                "release_date": {}
            }
        }
    }
    query["query"]["range"]["release_date"] = {"gte": start_date.strftime("%Y-%m-%d")}
    
    if end_date is not None:
        query["query"]["range"]["release_date"]["lte"] = end_date.strftime("%Y-%m-%d")
        
    response = es.search(index=INDEX, body=query)
    return parse_data(response, 0, PAGE_SIZE)

if __name__ == "__main__":
    uvicorn_config = {
        "app": "main:app",
        "host": BACKEND_HOST,
        "port": BACKEND_PORT
    }
    uvicorn.run(**uvicorn_config)
import time
import json
import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

init_elastic = bool(os.getenv("SLEEP_TIME"))

if init_elastic:
    print("Waiting for Elasticsearch")
    sleep_time = int(os.getenv("SLEEP_TIME"))
    time.sleep(sleep_time)
    print("Processing data...")
    data_dir = os.getenv("DATA_DIR")
    index_name = os.getenv("INDEX_NAME")
    elasticsearch_host = os.getenv("ELASTICSEARCH_HOST")
    es = Elasticsearch([elasticsearch_host])
    # Delete the index if it already exists
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print("Index " + index_name + " deleted")
    # Create the index if it does not exist
    if not es.indices.exists(index=index_name):
        settings = {"analysis": {
                "analyzer": {
                    "edge_ngram_analyzer": {
                    "tokenizer": "edge_ngram_tokenizer",
                    "filter": ["lowercase"]                # If text is not lowercased, this lowercase it. 
                    }
                },
                "tokenizer": {
                    "edge_ngram_tokenizer": {
                        "type": "edge_ngram",              # Partial match search
                        "min_gram": 2,                     # Minimum length of n-grams at the beggining of each word ("Mario" => "Ma", "Ring" => "Ri"...)
                        "max_gram": 20,                    # Maximum length of n-grams
                        "token_chars": ["letter", "digit"] # N-grams generated with letters and digits
                    }
                }
            }
        }
        mapping = {
            "properties": {
                "title": {"type": "text"},
                "title_search": {
                    "type": "text",
                    "analyzer": "edge_ngram_analyzer"
                },
                "title_keyword": {"type": "keyword"},
                "critic_reviews": {"type": "integer"},
                "genre": {"type": "keyword"},
                "metascore": {"type": "integer"},
                "release_date": {"type": "date", "format": "yyyy-MM-dd"},
                "summary": {"type": "text"},
                "url": {"type": "keyword"},
                "user_reviews": {"type": "integer"},
                "user_score": {"type": "float"},
                "images": {"type": "text"},
                "video": {"type": "text"},
                "video_type": {"type": "text"},
                "sentiment": {"type": "text"},
                "must_play": {"type": "text"},
                "crew": {"type": "text"},
                "countries": {"type": "keyword"},
                "companies": {"type": "text"},
                "platforms": {"type": "keyword"},
                "rating": {"type": "text"},
                "official_site": {"type": "keyword"}
            }
        }
        es.indices.create(index=index_name, body={"settings": settings, "mappings": mapping})
        print("Index " + index_name + " created")
    # Load the data to the index
    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        if os.path.isfile(file_path) and filename.endswith(".json"):
            try:
                with open(file_path, 'r') as f:
                    items = json.load(f)
                    for item in items:
                        es.index(index=index_name, body=item)
                    es.indices.refresh(index=index_name)
                print("Data loaded successfully! from partition: " + filename)
            except Exception as e:
                print(e)
else:
    print("Skipped data loading")




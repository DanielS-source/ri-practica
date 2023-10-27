# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import os
from elasticsearch import Elasticsearch
from metacritic.items import MetacriticItemEncoder
import threading
from scrapy.exceptions import DropItem
from metacritic.csv_parser import CSVParser

class ElasticsearchPipeline:
    items = []                                      # Item list
    threads = []                                    # Thread list
    data_item = 0                                   # Data partition index
    n_items = 0                                     # Items processed
    data_dir = "data"                               # Partition data directory
    data_path = "data-part-"+str(data_item)+".json" # Partition data file path

    def update_data_path(self):
        self.data_item += 1
        self.data_path = "data-part-"+str(self.data_item)+".json"

    def __init__(self, elastic_settings):
        self.elastic_settings = elastic_settings
        self.index_name = elastic_settings['index_name']
        self.es = Elasticsearch([elastic_settings['host']])
        self.delete_index()
        self.create_index()
        # Using os to create the data directory if it does not exist because of retrocompatibility
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def delete_index(self):
        if self.es.indices.exists(index=self.index_name) and self.elastic_settings['delete_index']:
            self.es.indices.delete(index=self.index_name)

    @classmethod
    def from_crawler(cls, crawler):
        elastic_settings = crawler.settings.getdict('ELASTICSEARCH')
        return cls(elastic_settings)
    
    def create_index(self):
        if not self.es.indices.exists(index=self.index_name):
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
            self.es.indices.create(index=self.index_name, body={"settings": settings, "mappings": mapping})

    def write_data(self, spider):
        spider.logger.debug("Writting data to file... "+ self.data_dir + "/"+  self.data_path)
        with open(self.data_dir + "/"+ self.data_path, 'w') as file:
            file.write(json.dumps(self.items))
        self.items = []
        self.update_data_path()

    def process_item(self, item, spider):
        max_items = spider.settings.getint('MAX_ITEMS_PROCESSED')
        items_partition = spider.settings.getint('ITEMS_PARTITION')
        first_item_page = spider.settings.getint('FIRST_ITEM_PAGE')
        if (self.data_item < first_item_page):
            self.data_item = first_item_page
        if self.n_items < max_items:
            data = dict(item)
            # Save the item in elastic
            self.es.index(index=self.index_name, body=data)
            # Save the item in the items list
            self.items.append(json.dumps(item, cls=MetacriticItemEncoder))

            # Save the partition
            if len(self.items) == items_partition:
                writer = threading.Thread(target=self.write_data(spider))
                writer.start()
                self.threads.append(writer)
            self.n_items += 1
            spider.logger.debug("-------------------------------------------------------------------------")
            spider.logger.debug("\t\t\tItems processed: " + str(self.n_items) + " / " + str(max_items) + " | " + str(max_items-self.n_items) + " left")
            spider.logger.debug("-------------------------------------------------------------------------")
            if spider.current_url is not None:
                spider.logger.debug("\t\t\t"+spider.current_url)
                spider.logger.debug("-------------------------------------------------------------------------")
            return item
        else:
            spider.start_urls = []
            spider.urls = []
            spider.data_extracted = False
            spider.extracting = False
            spider.crawler.engine.close_spider(spider, 'crawling_stopped')

            raise DropItem("Crawling stopped due to reached máx. items.")
    

    # In this function we check if data partitions exist and load them
    def load_data_partitions(self, spider):
        for filename in os.listdir(self.data_dir):
            file_path = os.path.join(self.data_dir, filename)
            if os.path.isfile(file_path) and filename.endswith(".json"):
                try:
                    with open(file_path, 'r') as f:
                        items = json.load(f)
                        for item in items:
                            self.es.index(index=self.index_name, body=item)
                        self.es.indices.refresh(index=self.index_name)
                    spider.logger.debug("Data loaded successfully! from partition: " + filename)
                except Exception as e:
                    spider.logger.error(e)

    def close_spider(self, spider):
        if len(self.items) == 0 and self.n_items < spider.settings.getint('MAX_ITEMS_PROCESSED'):
            spider.logger.debug("Loading data from file(s)...")
            self.load_data_partitions(spider)
        else:
            # Items that not fill the partition will be written in another file to avoid losing data
            writer = threading.Thread(target=self.write_data(spider))
            self.threads.append(writer)
            writer.start()
            # Wait until all threads are finished
            for thread in self.threads:
                thread.join()
            # Transform the data into a CSV file
            spider.logger.debug("Transforming data into CSV file...")
            CSVParser()
            

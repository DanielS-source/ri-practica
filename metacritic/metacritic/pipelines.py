# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from elasticsearch import Elasticsearch

class ElasticsearchPipeline:
    def __init__(self, elastic_settings):
        self.elastic_settings = elastic_settings
        self.index_name = elastic_settings['index_name']
        self.es = Elasticsearch([elastic_settings['host']])
        if self.es.indices.exists(index=self.index_name) and elastic_settings['delete_index']:
            self.es.indices.delete(index=self.index_name)
        self.create_index()

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

    def process_item(self, item, spider):
        data = dict(item)
        self.es.index(index=self.index_name, body=data)
        return item




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
        if elastic_settings['delete_index']:
            self.es.indices.delete(index=self.index_name)
        self.create_index()

    @classmethod
    def from_crawler(cls, crawler):
        elastic_settings = crawler.settings.getdict('ELASTICSEARCH')
        return cls(elastic_settings)
    
    def create_index(self):
        if not self.es.indices.exists(index=self.index_name):
            mapping = {
                "properties": {
                    "critic_reviews": {"type": "integer"},
                    "genre": {"type": "keyword"},
                    "metascore": {"type": "integer"},
                    "producer": {"type": "keyword"},
                    "release_date": {"type": "date", "format": "yyyy-MM-dd"},
                    "summary": {"type": "text"},
                    "title": {"type": "text"},
                    "url": {"type": "keyword"},
                    "user_reviews": {"type": "integer"},
                    "user_score": {"type": "float"}
                }
            }
            self.es.indices.create(index=self.index_name, body={"mappings": mapping})

    def process_item(self, item, spider):
        data = dict(item)
        self.es.index(index=self.index_name, body=data)
        return item




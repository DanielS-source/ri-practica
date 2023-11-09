# Scrapy settings for metacritic project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "metacritic"

SPIDER_MODULES = ["metacritic.spiders"]
NEWSPIDER_MODULE = "metacritic.spiders"

################################
#       CUSTOM SETTINGS        #
################################
SHOULD_STOP = False            # Boolean shared if the crawler should stop
FIRST_ITEM_PAGE = 0            # First item page     
MAX_ITEMS_PROCESSED = 500      # Max items that will be processed 
ITEMS_PARTITION = 100          # Number of items per partition
HTTPERROR_ALLOWED_CODES = [404]# List of allowed HTTP error codes
RETRY_HTTP_CODES = [500, 443]  # List of HTTP error codes to retry retrieving info
RETRY_TIMES = 3                # The amount of retry times
################################

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "RIWS-MUEI-FIC-UDC Scrappy Bot - Course Assignment"
#USER_AGENT = "Mozilla/5.0 (Nintendo Switch; WebApplet) AppleWebKit/609.4 (KHTML, like Gecko) NF/6.0.2.21.3 NintendoBrowser/5.1.0.22474"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Disable duplication exception
DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 8

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3 # Not configured because autothrottle is enabled
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 8

#DEPTH_LIMIT = 10

# Disable cookies (enabled by default)
#COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "metacritic.middlewares.MetacriticSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "metacritic.middlewares.MetacriticDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "metacritic.pipelines.MetacriticPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 3
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 6
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

ITEM_PIPELINES = {
    'metacritic.pipelines.ElasticsearchPipeline': 100,
}

ELASTICSEARCH = {
    'host': 'http://elastic:riwspractica@localhost:9200',
    'index_name': 'metacritic',
    'delete_index': True  # Set to True if you want to delete the existing index
}

DOWNLOADER_MIDDLEWARES = {
    # Random user agents
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'metacritic.middlewares.UserAgentMiddleware': 120000,
}

USER_AGENTS_LIST = 'user-agents/user-agent-list.txt'

CHARSET_DETECTION_OVERRIDE = 'utf-8'

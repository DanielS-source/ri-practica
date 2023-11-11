from pathlib import Path
from anyio import sleep
import scrapy
import re
from metacritic.items import MetacriticItem
from datetime import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
import jsbeautifier
import json
from unidecode import unidecode

class MetacriticSpiderSpider(scrapy.Spider):
    name = "metacritic_spider"
    allowed_domains = ["metacritic.com", "fandom-prod.apigee.net"]
    start_urls = []
    data_dir = "data"
    image_path = "https://www.metacritic.com/a/img/catalog"
    video_path = "https://cdn.jwplayer.com/v2/media/"
    sitemap_urls = [
        'http://metacritic.com/games.xml'
    ]
    urls = []
    current_url = None
    extracting = False
    data_extracted = False
    page = None

    rules = (
        Rule(
            LinkExtractor(deny=('.*\.txt', '.*\.png', '.*\.jpg', '.*\.jpeg', '.*\.gif', '.*\.mp4', '.*\.html', '.*\.m3u8')),
            callback='parse_sitemap',
            follow=False
        ),
    )

    # Transforms the string to lowercase and then removes special characters, leaving only letters, numbers and spaces.
    def normalize_string_lower(self, input_string):    
        return re.sub(r'[^a-zA-Z0-9\s]', '', unidecode(input_string.lower()))
    
    def normalize_string(self, input_string):
        data = input_string.strip()
        if data.startswith('Metacritic'):
            return None
        else:
            data = data.replace(' ?', '').replace('??', '').replace('_', ' ')
            data = data.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
            data = re.sub(r'(https?://[a-zA-Z0-9.\/]+)', r'<a href="\1" target="_blank">\1</a>', data)
            return data
    
    def start_requests(self):
        if not any(Path(self.data_dir).iterdir()):
            try:
                yield scrapy.Request(self.sitemap_urls[0], callback=self.get_start_urls, dont_filter = True)
            except:
                self.logger.error("Crawling not started!")
                return
        else:
            self.logger.info("Crawling not started because data partitions exist! Preparing for loading data from data partitions...")

    async def get_start_urls(self, response): 
        first_item_page = self.settings.getint('FIRST_ITEM_PAGE', 0)
        for url in self.get_loc_label(response):
            if url[-3:] == "xml":
                match = re.search(r'/(\d+)\.xml', url)
                if match:
                    number = int(match.group(1))
                    if number >= first_item_page:
                        self.start_urls.append(url)
                        
        while (len(self.start_urls) > 0):
            if not self.extracting:
                self.extracting = True
                try:
                    self.current_url = self.start_urls.pop(0)
                    yield response.follow(self.current_url, callback=self.parse_sitemap)
                except:
                    self.extracting = False
            # Sleep for 0.65 second to process the next request in order.
            await sleep(0.65)

    def get_loc_label(self, response):
        # Parse the XML with BeautifulSoup
        soup = BeautifulSoup(response.body, 'xml')

        # Find all labels <loc> inside the labels <sitemap>
        loc_tags = soup.find_all('loc')

        urls = [loc.text for loc in loc_tags]

        return urls

    def handle_httpstatus(self, response):
        # Add more handlers if necessary
        if response.status == 404:
            self.data_extracted = False
    
    async def parse_sitemap(self, response):
        try:
            #for url in self.get_loc_label(response):
            self.urls = self.get_loc_label(response)
            while (len(self.urls) > 0):
            # Create a request to fetch the next URL
                if not self.data_extracted:
                    self.data_extracted = True
                    try:
                        yield scrapy.Request(self.urls.pop(0), callback=self.parse_data)
                    except:
                        self.data_extracted = True 
                # Sleep for 0.65 second to process the next request in order.
                await sleep(0.65)
            self.extracting = False
        except Exception as e:
            self.logger.error("Item not crawled!")
            self.logger.error(e) 
            return

    def parse_data(self, response):
        item = MetacriticItem()
        ## GENERAL ITEMS
        # Product title
        title = response.css('.c-productHero_title div::text').get()
        item['title'] = (title.strip() if title else None)
        item['title_search'] = (self.normalize_string_lower(title.strip()) if title else None)
        item['title_keyword'] = (self.normalize_string_lower(title.strip()) if title else None)

        # Metacritic url
        item['url'] = response.url.strip()

        # Description of the product
        description = response.css('meta[name="description"]::attr(content)').get()
        
        item['summary'] = (self.normalize_string(description) if description else None)
           
        # Genres of the product
        genres_list = response.css('.c-genreList_item a.c-globalButton_container span.c-globalButton_label::text').getall()
        item['genre'] = ([genre.strip() for genre in genres_list] if genres_list else None)

        # Critics average score
        metascore = response.css('.c-productScoreInfo_scoreNumber span::text').get()
        item['metascore'] = (metascore.strip() if (metascore and str(metascore) != 'tbd') else 0)

        # Critic reviews count
        critic_reviews_count_text = response.css('.c-productScoreInfo_reviewsTotal a span::text').get()
        try:
            match = (re.search(r'\d+', critic_reviews_count_text) if critic_reviews_count_text else False)
            critic_reviews_count = int(match.group())
        except:
            match = False
        item['critic_reviews'] = (critic_reviews_count if match else 0)
        
        # Users average score
        # Often critics have earlier access to the product so there may be a situation where no user score is available
        user_score = response.css('.c-siteReviewScore_background-user span[data-v-4cdca868]::text').get()
        try:
            user_score = (user_score.strip() if user_score else 0)
        except:
            user_score = None
        item['user_score'] = (0 if str(user_score).lower() == 'tbd' and user_score else user_score)

        # User reviews count
        user_reviews_count_text = response.css('.c-productScoreInfo_reviewsTotal a span::text')
        if len(user_reviews_count_text) >= 2:
            match = re.search(r'\d+', user_reviews_count_text[1].get())
            if match:
                user_reviews_count = int(match.group())
                item['user_reviews'] = user_reviews_count
            else:
                item['user_reviews'] = 0
        else:
            item['user_reviews'] = 0

        # If meta score is the same as user score, then it means that meta score is using the user score value (Same class in this elements).
        if metascore == user_score:
            item['metascore'] = 0
            item['user_reviews'] = item['critic_reviews']
            item['critic_reviews'] = 0

        ## SPECIFIC ITEMS
        if "/game/" in response.url:
            ### GAMES ONLY
            release_date = response.css('.c-gameDetails_ReleaseDate span.g-outer-spacing-left-medium-fluid::text').get()
            if release_date:
                try:
                    date_obj = datetime.strptime(release_date.strip(), "%b %d, %Y")
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    item['release_date'] = formatted_date
                except ValueError:
                    item['release_date'] = None

            # Producer of the product. 
            # In videogames we take the developer and publisher
            developers = response.css('.c-gameDetails_Developer ul li::text').getall()
            publishers = response.css('.c-gameDetails_Distributor span.g-outer-spacing-left-medium-fluid::text').getall()
            producers_and_publishers = set()
            if developers:
                producers_and_publishers.update([(item.strip() + " (Developer)") for item in developers])
            if publishers:
                producers_and_publishers.update([(item.strip() + " (Publisher)") for item in publishers])
            item['companies'] = list(producers_and_publishers)
            
        # Scrap Metacritic API script to get additional information and return the item.
        return self.find_api_script(response, item)

    # Scrapping Metacritic API
    def find_api_script(self, response, item):
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tags = soup.find_all('script')[10]
        start_index = 'k.components = [{'
        end_index = 'item:'
        start_index_2 = 'href: "'
        end_index_2 = '"'
        script_content = script_tags.get_text()
        beautified_code = jsbeautifier.beautify(script_content)
        start_pos = beautified_code.find(start_index)
        end_pos = beautified_code.find(end_index)
        # self.logger.debug('Finding API script... in ' + response.url)
        if start_pos != -1 and end_pos != -1:
            result = beautified_code[start_pos + len(start_index):end_pos].strip()
            start_pos_2 = result.find(start_index_2)
            end_pos_2 = result[start_pos_2 + len(start_index_2):].find(end_index_2)
            result = result[start_pos_2 + len(start_index_2):start_pos_2 + len(start_index_2) + end_pos_2].strip()
            result = result.replace("\\u002F", "/").replace('",', '')
            return response.follow(result, callback=self.parse_api, cb_kwargs={'item': item})
        else:
            self.logger.debug('Nothing found in ' + response.url)
            item['images'] = []
            item['video'] = None
            item['video_thumbnail'] = None
            item['video_type'] = None
            item['sentiment'] = None
            item['must_play'] = False
            item['crew'] = None
            item['countries'] = None
            item['platforms'] = None
            item['rating'] = None
            self.data_extracted = False
            return item

    def parse_api(self, response, item):
        data = json.loads(response.text)
        formatted_json = json.dumps(data, indent=4)
        images = []
        if len(data["data"]["item"]["images"]) > 0:
            img = data["data"]["item"]["images"][1]["bucketPath"]
            img_poster = data["data"]["item"]["images"][0]["bucketPath"]
            images.append(self.image_path + img)
            images.append(self.image_path + img_poster)
       
        item['images'] = images
        video = ""
        video_type = "application/x-mpegURL"

        item['sentiment'] = (None if "sentiment" not in data["data"]["item"]["criticScoreSummary"] else data["data"]["item"]["criticScoreSummary"]["sentiment"])
        item['must_play'] = (False if "mustPlay" not in data["data"]["item"] else data["data"]["item"]["mustPlay"])

        crew = []
        if "crew" in data["data"]["item"]["production"]:
            for c in data["data"]["item"]["production"]["crew"]:
                crew_member = c["name"] + " (" + ', '.join(c["roles"]) + ")"
                crew.append(crew_member)

        item['crew'] = (None if crew == [] else crew)
        item['countries'] = (None if "countries" not in data["data"]["item"] else data["data"]["item"]["countries"])

        platforms = []
        if "platforms" in data["data"]["item"]:
            for platform in data["data"]["item"]["platforms"]:
                platforms.append(platform["name"])
        item['platforms'] = (None if platforms == [] else platforms)

        item['rating'] = (None if data["data"]["item"]["rating"] == "null" else data["data"]["item"]["rating"])

        # We don't use the api anymore to retrieve videos
        """if "officialSite" in data["data"]["item"]["production"]:
            item['official_site'] = (None if data["data"]["item"]["production"]["officialSite"] == "null" else data["data"]["item"]["production"]["officialSite"])
        elif "officialSiteUrl" in data["data"]["item"]["production"]:
            item['official_site'] = (None if data["data"]["item"]["production"]["officialSiteUrl"] == "null" else data["data"]["item"]["production"]["officialSiteUrl"])"""

        if data["data"]["item"]["video"] != None:
            if "url" in data["data"]["item"]["video"]:
                item['video'] = data["data"]["item"]["video"]["url"]
                item["video_thumbnail"] = None
                item['video_type'] = "video/mp4" 
            else:
                video = data["data"]["item"]["video"]["videoLinks"][0]["videoLinks"][0]["linkUrl"]
                return response.follow(self.video_path+video, callback=self.get_video_info, cb_kwargs={'item': item}, dont_filter=True)
            
        else:
            item['video'] = None
            item['video_thumbnail'] = None
            item['video_type'] = None
            self.data_extracted = False
        return item

    
    # Finally get the video information
    def get_video_info(self, response, item):
        video_data = json.loads(response.text)
        video_title = video_data['title']
        video_description = video_data['description']
        if "playlist" not in video_data and "sources" not in video_data:
            return item
        video_duration = video_data['playlist'][0]['duration']
        # Video thumbnails are sorted by default from low quality to high quality
        video_thumbnails = list(video_data['playlist'][0]['images'])

        if len(video_thumbnails) > 0:
            item['video_thumbnail'] = video_thumbnails[0]['src'] # Reverse thumbnail list to get the highest quality thumbnail
        else:
            item['video_thumbnail'] = video_data['playlist'][0]['image'] # Get default video thumbnail

        video_file = video_data['playlist'][0]['sources'][0]['file']
        video_type = video_data['playlist'][0]['sources'][0]['type']

        item['video'] = (video_file if video_file else None)
        item['video_type'] = (video_type if video_type else None)
        
        self.data_extracted = False
        return item
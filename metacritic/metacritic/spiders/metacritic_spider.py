import scrapy
import re
from metacritic.items import MetacriticItem
from datetime import datetime
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup
import jsbeautifier
import json


class MetacriticSpiderSpider(scrapy.Spider):
    name = "metacritic_spider"
    allowed_domains = ["metacritic.com", "fandom-prod.apigee.net"]
    start_urls = ["https://www.metacritic.com/movie/no-one-will-save-you/", "https://www.metacritic.com/tv/breaking-bad/", "https://www.metacritic.com/game/cyberpunk-2077-phantom-liberty/", "https://www.metacritic.com/game/payday-3/"]
    #start_urls = ["https://www.metacritic.com/game/cyberpunk-2077-phantom-liberty/", "https://www.metacritic.com/game/payday-3/"]
    #start_urls = ["https://www.metacritic.com/movie/no-one-will-save-you/"]
    #start_urls = ["https://www.metacritic.com/tv/breaking-bad/"]

    def parse(self, response):
        item = MetacriticItem()
        ## GENERAL ITEMS
        # Product title
        title = response.css('.c-productHero_title div::text').get()
        item['title'] = (title.strip() if title else None)

        # Metacritic url
        item['url'] = response.url.strip()

        # Description of the product
        description = response.css('meta[name="description"]::attr(content)').get()
        item['summary'] = (description if description else None)
           
        # Genres of the product
        genres_list = response.css('.c-genreList_item a.c-globalButton_container span.c-globalButton_label::text').getall()
        item['genre'] = ([genre.strip() for genre in genres_list] if genres_list else None)

        # Critics average score
        metascore = response.css('.c-productScoreInfo_scoreNumber span::text').get()
        item['metascore'] = (metascore.strip() if metascore else None)

        # Critic reviews count
        critic_reviews_count_text = response.css('.c-productScoreInfo_reviewsTotal a span::text').get()
        match = (re.search(r'\d+', critic_reviews_count_text) if critic_reviews_count_text else False)
        critic_reviews_count = int(match.group())
        item['critic_reviews'] = (critic_reviews_count if match else None)
        
        # Users average score
        # Often critics have earlier access to the product so there may be a situation where no user score is available
        user_score = response.css('.c-siteReviewScore_background-user span[data-v-4cdca868]::text').get()
        user_score = (user_score.strip() if user_score else None)
        item['user_score'] = (None if user_score.lower() == 'tbd' and user_score != None else user_score)

        # User reviews count
        user_reviews_count_text = response.css('.c-productScoreInfo_reviewsTotal a span::text')
        if len(user_reviews_count_text) >= 2:
            match = re.search(r'\d+', user_reviews_count_text[1].get())
            if match:
                user_reviews_count = int(match.group())
                item['user_reviews'] = user_reviews_count
            else:
                item['user_reviews'] = None
        else:
            item['user_reviews'] = None

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
                producers_and_publishers.update([item.strip() for item in developers])
            if publishers:
                producers_and_publishers.update([item.strip() for item in publishers])
            item['producer'] = list(producers_and_publishers)

        if "/movie/" in response.url:
            ### MOVIES ONLY
            # Producer and date of the product. 
            movieDetails = response.css('.c-movieDetails_sectionContainer span.g-outer-spacing-left-medium-fluid::text')
            if len(movieDetails) >= 1:
                publisher = movieDetails[0].get().strip()
                publishers = [x.strip() for x in publisher.split(',')]
                item['producer'] = publishers
                if len(movieDetails) >= 2:
                    release_date = movieDetails[1].get().strip()
                    try:
                        date_obj = datetime.strptime(release_date.strip(), "%b %d, %Y")
                        formatted_date = date_obj.strftime("%Y-%m-%d")
                        item['release_date'] = formatted_date
                    except ValueError:
                        item['release_date'] = None
                else:
                    item['release_date'] = None
            else:
                item['producer'] = None
                item['release_date'] = None
        
        if "/tv/" in response.url:
            ### TV ONLY
            # Producer of the product. 
            production = response.css('.c-productionDetailsTv_sectionContainer ul.g-outer-spacing-left-medium-fluid li.c-productionDetailsTv_listItem::text').getall()
            if production:
                production_list = set()
                production_list.update([item.strip() for item in production if item.strip()])
                item['producer'] = list(production_list)
            else:
                item['producer'] = None

            # Date of the product. 
            release_date = response.css('.c-productionDetailsTv_sectionContainer span.g-outer-spacing-left-medium-fluid::text').get()
            if release_date:
                try:
                    date_obj = datetime.strptime(release_date.strip(), "%b %d, %Y")
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    item['release_date'] = formatted_date
                except ValueError:
                    item['release_date'] = None

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
        self.logger.debug('Finding API script... in ' + response.url)
        if start_pos != -1 and end_pos != -1:
            result = beautified_code[start_pos + len(start_index):end_pos].strip()
            start_pos_2 = result.find(start_index_2)
            end_pos_2 = result[start_pos_2 + len(start_index_2):].find(end_index_2)
            result = result[start_pos_2 + len(start_index_2):start_pos_2 + len(start_index_2) + end_pos_2].strip()
            result = result.replace("\\u002F", "/").replace('",', '')
            return response.follow(result, callback=self.parse_api, cb_kwargs={'item': item})
        else:
            self.logger.debug('Nothing found')
            item['images'] = None
            item['video'] = None
            item['video_type'] = None
            item['sentiment'] = None
            item['must_play'] = False
            item['cast_crew'] = None
            item['countries'] = None
            item['companies'] = None
            item['platforms'] = None
            item['rating'] = None
            item['seasons'] = 0
            item['official_site'] = None
            return item

    def parse_api(self, response, item):
        data = json.loads(response.text)
        formatted_json = json.dumps(data, indent=4)
        img = data["data"]["item"]["images"][1]["bucketPath"]
        img_poster = data["data"]["item"]["images"][0]["bucketPath"]
        img_ext = "jpg"
        item['images'] = img +", "+img_poster
        video = ""
        video_type = "application/x-mpegURL"

        item['sentiment'] = (None if "sentiment" not in data["data"]["item"]["criticScoreSummary"] else data["data"]["item"]["criticScoreSummary"]["sentiment"])
        item['must_play'] = (False if "mustPlay" not in data["data"]["item"] else data["data"]["item"]["mustPlay"])

        cast_crew = []
        if "cast" in data["data"]["item"]["production"]:
            for cast in data["data"]["item"]["production"]["cast"]:
                cast_member = cast["name"] + " (" + ', '.join(cast["roles"]) + ")"
                cast_crew.append(cast_member)
        elif "crew" in data["data"]["item"]["production"]:
            for crew in data["data"]["item"]["production"]["crew"]:
                crew_member = crew["name"] + " (" + ', '.join(crew["roles"]) + ")"
                cast_crew.append(crew_member)

        item['cast_crew'] = (None if cast_crew == [] else cast_crew)
        item['countries'] = (None if "countries" not in data["data"]["item"] else data["data"]["item"]["countries"])

        companies = []
        if "companies" in data["data"]["item"]["production"]:
            for company in data["data"]["item"]["production"]["companies"]:
                companies.append(company["name"] + (None if company["typeName"] == "null" else " - (" + company["typeName"])  + ")")       
        item['companies'] = (None if companies == [] else companies)

        platforms = []
        if "platforms" in data["data"]["item"]:
            for platform in data["data"]["item"]["platforms"]:
                platforms.append(platform["name"])
        item['platforms'] = (None if platforms == [] else platforms)

        item['rating'] = (None if data["data"]["item"]["rating"] == "null" else data["data"]["item"]["rating"])

        if "officialSite" in data["data"]["item"]["production"]:
            item['official_site'] = (None if data["data"]["item"]["production"]["officialSite"] else data["data"]["item"]["production"]["officialSite"])
        elif "officialSiteUrl" in data["data"]["item"]["production"]:
            item['official_site'] = (None if data["data"]["item"]["production"]["officialSiteUrl"] == "null" else data["data"]["item"]["production"]["officialSiteUrl"]) 
        item['seasons'] = (0 if "seasonCount" not in data["data"]["item"] else data["data"]["item"]["seasonCount"])

        if data["data"]["item"]["video"] != None:
            if "url" in data["data"]["item"]["video"]:
                video = data["data"]["item"]["video"]["url"]
                video_type = "video/mp4" 
            else:
                video = data["data"]["item"]["video"]["videoLinks"][0]["videoLinks"][0]["linkUrl"]
                video = video + ".m3u8"
            item['video'] = video
            item['video_type'] = video_type
        else:
            self.logger.debug('Nothing found')
            item['images'] = None
            item['video'] = None
            item['video_type'] = None

        return item
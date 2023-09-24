import scrapy
import re
from metacritic.items import MetacriticItem
from datetime import datetime
from scrapy.spiders import CrawlSpider, Rule


class MetacriticSpiderSpider(scrapy.Spider):
    name = "metacritic_spider"
    allowed_domains = ["metacritic.com"]
    start_urls = ["https://www.metacritic.com/movie/no-one-will-save-you/", "https://www.metacritic.com/tv/breaking-bad/", "https://www.metacritic.com/game/cyberpunk-2077-phantom-liberty/", "https://www.metacritic.com/game/payday-3/"]
    #start_urls = ["https://www.metacritic.com/game/cyberpunk-2077-phantom-liberty/", "https://www.metacritic.com/game/payday-3/"]
    #start_urls = ["https://www.metacritic.com/movie/no-one-will-save-you/"]
    #start_urls = ["https://www.metacritic.com/tv/breaking-bad/"]

    def parse(self, response):
        item = MetacriticItem()

        ## GENERAL ITEMS

        # Product title
        title = response.css('.c-productHero_title div::text').get()
        if title:
            item['title'] = title.strip()

        # Metacritic url
        item['url'] = response.url.strip()

        # Description of the product
        description = response.css('meta[name="description"]::attr(content)').get()
        if description:
            item['summary'] = description 
           
        # Genres of the product
        genres_list = response.css('.c-genreList_item a.c-globalButton_container span.c-globalButton_label::text').getall()
        if genres_list:
            item['genre'] = [genre.strip() for genre in genres_list]

        # Critics average score
        metascore = response.css('.c-productScoreInfo_scoreNumber span::text').get()
        if metascore:
            item['metascore'] = metascore.strip()

        # Critic reviews count
        critic_reviews_count_text = response.css('.c-productScoreInfo_reviewsTotal a span::text').get()
        if critic_reviews_count_text:
            match = re.search(r'\d+', critic_reviews_count_text)
            if match:
                critic_reviews_count = int(match.group())
                item['critic_reviews'] = critic_reviews_count
            else:
                item['critic_reviews'] = None
        
        # Users average score
        # Often critics have earlier access to the product so there may be a situation where no user score is available
        user_score = response.css('.c-siteReviewScore_background-user span[data-v-4cdca868]::text').get()
        if user_score:
            user_score = user_score.strip()
            if user_score.lower() == 'tbd':
                item['user_score'] = None
            else:
                item['user_score'] = user_score
        else:
            item['user_score'] = None

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
                    formatted_date = date_obj.strftime("%d/%m/%Y")
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
                        formatted_date = date_obj.strftime("%d/%m/%Y")
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
                    formatted_date = date_obj.strftime("%d/%m/%Y")
                    item['release_date'] = formatted_date
                except ValueError:
                    item['release_date'] = None

        print(item)
        yield item

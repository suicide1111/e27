import csv
import random
from ..items import E27Item
import scrapy
from scrapy import Request
import datetime

stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

class E27Spider(scrapy.Spider):
    name = 'e27_datails'
    allowed_domain = 'e27.co'
    base_url = 'https://e27.co/startups/'
    custom_settings = {
        "DOWNLOAD_DELAY": 0.3,
        # "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        'FEED_FORMAT': "csv",
        'FEED_URI': f"{name}_{stamp}.csv",
        'LOG_LEVEL': 'INFO',
    }

    start_urls = ['https://e27.co/api/startups/?all_fundraising=&pro=0&tab_name=recentlyupdated&start=0&length=10']

    def start_requests(self):

        with open("e27_links_2020-06-26-12-37-39.csv", "r", encoding='UTF-8') as f:
            reader = csv.DictReader(f)
            ran_link = random.choices(list(reader), k=250)
            for row in ran_link:
                name = row.get('name')
                slug = row.get('slug')
                link = row.get('Link')
                url = f'https://e27.co/api/startups/get/?slug={slug}&data_type=general&get_badge=true'
                yield Request(url, callback=self.parse, meta={'link': link})

    def parse(self, response):
        item = E27Item()
        data_json = response.json()
        id = data_json['data']['id']

        try:
            company_name = data_json['data']['metas']['name']
        except KeyError as e:
            company_name = None
            print(e)

        try:
            profile_url = response.meta['link']
        except KeyError as e:
            profile_url = None
            print(e)

        try:
            company_website_url = data_json['data']['metas']['website']
        except KeyError as e:
            company_website_url = None
            print(e)

        try:
            location = data_json['data']['location'][0]['text']
        except KeyError as e:
            location = None
            print(e)

        try:
            tags = data_json['data']['market']
            tags = tags.strip().replace('[[', '').replace(']]', '').replace('"', '').replace(',', ', ')
        except (KeyError, AttributeError) as e:
            tags = None
            print(e)

        founding_date = []
        try:
            found_year = data_json['data']['metas']['found_year']
            founding_date.append(found_year)
            found_month = data_json['data']['metas']['found_month']
            founding_date.append(found_month)
            founding_date = '-'.join(founding_date)
            founding_date = datetime.datetime.strptime(founding_date, "%Y-%m").strftime("%Y-%m-%d")
        except (KeyError, ValueError, UnboundLocalError) as e:
            founding_date = None
            print(e)

        founders = []
        try:
            founders_len = len(data_json['data']['metas']['sub_owner'])
            for i in range(founders_len):
                founders.append(data_json['data']['metas']['sub_owner'][i])
        except (KeyError, ValueError) as e:
            print(e)

        try:
            employee_range = data_json['data']['metas']['employee_range']
        except (KeyError, ValueError) as e:
            employee_range = None
            print(e)

        urls = []
        try:
            twitter = data_json['data']['metas']['twitter']
            if len(twitter) > 3:
                twitter = 'https://twitter.com/' + twitter
                urls.append(twitter)
        except KeyError as e:
            twitter = None
            print(e)

        try:
            facebook = data_json['data']['metas']['facebook']
            if facebook != None:
                urls.append(facebook)
        except KeyError as e:
            print(e)

        try:
            linkedin = data_json['data']['metas']['linkedin']
            if linkedin != None:
                urls.append(linkedin)
        except KeyError as e:
            print(e)
        urls = ','.join(urls)

        try:
            emails = data_json['data']['metas']['email']
        except KeyError as e:
            emails = None
            print(e)

        try:
            phones = data_json['data']['metas']['phone']
        except KeyError as e:
            phones = None
            print(e)

        try:
            description_short = data_json['data']['metas']['short_description']
            description_short = description_short.strip().replace('\n\n', ' ').replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
        except (KeyError, UnboundLocalError) as e:
            description_short = None
            print(e)

        try:
            description = data_json['data']['metas']['description']
            description = description.strip().replace('\n\n', ' ').replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
        except (KeyError, UnboundLocalError) as e:
            description = None
            print(e)

        item['company_name'] = company_name
        item['profile_url'] = profile_url
        item['company_website_url'] = company_website_url
        item['location'] = location
        item['tags'] = tags
        item['founding_date'] = founding_date
        # item['founders'] = founders
        item['employee_range'] = employee_range
        item['urls'] = urls
        item['emails'] = emails
        item['phones'] = phones
        item['description_short'] = description_short
        item['description'] = description

        url_founders_detailed = f'https://e27.co/api/site_user_startups/site_users/?startup_id={id}'

        if founders != [] or [None]:
            yield Request(url_founders_detailed,
                          meta={'item': item, 'founders': founders},
                          callback=self.parse_founders)
        else:
            item['founders'] = founders
            yield item

    def parse_founders(self, response):
        data_json = response.json()
        founders_detailed = []
        founders = response.meta['founders']
        json_len = len(data_json['data']['site_users'])
        for i in range(json_len):
            site_user_id = data_json['data']['site_users'][i]['site_user_id']
            for founder in founders:
                if founder == site_user_id:
                    founder_name = data_json['data']['site_users'][i]['name']
                    founders_detailed.append(founder_name)

        detailed_item = response.request.meta['item']
        detailed_item['founders'] = founders_detailed
        yield detailed_item
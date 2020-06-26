import scrapy
from scrapy import Request
from datetime import datetime

dt = datetime.now()
stamp = dt.strftime("%Y-%m-%d-%H-%M-%S")


class E27Spider(scrapy.Spider):
    name = 'e27_links'
    allowed_domain = 'e27.co'
    base_url = 'https://e27.co/startups/'
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        # "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        'FEED_FORMAT': "csv",
        'FEED_URI': f"{name}_{stamp}.csv"
    }

    start_urls = ['https://e27.co/api/startups/?all_fundraising=&pro=0&tab_name=recentlyupdated&start=0&length=10']

    def start_requests(self):
        total_links = 34414
        start = 0
        length = 500

        tl = float(total_links)
        tl = (round(tl, 2))

        x = tl / length
        x = int(x)

        for i in range(x):
            url = f'https://e27.co/api/startups/?all_fundraising=&pro=0&tab_name=recentlyupdated&start={start}&length={length}'
            start += length
            yield Request(url, callback=self.parse)

    def parse(self, response):
        data_json = response.json()
        json_len = len(data_json['data']['list'])
        try:
            for i in range(json_len):
                name = data_json['data']['list'][i]['name']
                link_name = data_json['data']['list'][i]['slug']
                link = self.base_url + link_name
                yield {
                    'name': name,
                    'slug': link_name,
                    'Link': link,
                }
        except IndexError as e:
            print(e)

import scrapy
from tutorial.items import IcffItem


class IcffSpider(scrapy.Spider):
    name = 'icff'
    allowed_domains = ['icff.com']
    start_urls = ['http://www.icff.com/show/floor-planexhibitors-list/?terms=&floor=Floor&category=Furniture']


    def parse(self, response):
        # filename = response.url.split('/')[-2] + '.html'
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        for x in response.xpath('//ul[@class="exhibitors"]/li/div[2]/ul'):
            item = IcffItem()
            item['name'] = x.xpath('li')[0].xpath('span/text()').extract()
            item['phone'] = x.xpath('li')[2].xpath('span/text()').extract()
            tmp = x.xpath('li')[4].xpath('a/@href').extract()
            item['email'] = tmp[0]
            item['email'] = item['email'].split('mailto:')[-1]
            item['website'] = tmp[-1]
            yield item

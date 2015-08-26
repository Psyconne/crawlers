import scrapy
from scrapy import Request
from tutorial.items import YellowItem


class YellowSpider(scrapy.Spider):
    name = 'yellow'
    allowed_domains = ['yellowpages.com.au']
    start_urls = ['https://www.yellowpages.com.au/search/listings?clue=Hairdressers&locationClue=&lat=&lon=&selectedViewMode=list',
                  'https://www.yellowpages.com.au/search/listings?clue=Beauty+Salons&locationClue=&lat=&lon=&selectedViewMode=list']

    def parse(self, response):
        # filename = response.url.split('/')[-2] + '.html'
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        for x in response.xpath('//div[@class="flow-layout outside-gap-large inside-gap inside-gap-large vertical"]/div[@class="cell in-area-cell middle-cell"]'):
            item = YellowItem()
            tmp = x.xpath('div/@data-business-name').extract()
            item['name'] = tmp[0].replace('_', ' ')
            item['address'] = x.css('div.poi-and-body > div > p::text').extract()
            item['phone'] = x.css('span.contact-text')[0].xpath('text()').extract()
            item['email'] = x.css('div.call-to-action-group')[1].css('a::attr(data-email)').extract()or x.xpath('div/div/div/div/div[3]/div[1]/a/@data-email').extract()
            yield item

        next_page = response.css('div.search-pagination-container > div').xpath('a[contains(text(),"Next ")]/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield Request(url, self.parse)

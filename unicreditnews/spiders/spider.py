import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import UnicreditnewsItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class UnicreditnewsSpider(scrapy.Spider):
	name = 'unicreditnews'
	start_urls = ['https://www.unicreditbulbank.bg/bg/za-nas/media/novini/?page=1']

	def parse(self, response):
		post_links = response.xpath('//h2/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//p[@class="text-center live-button"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):

		date = response.xpath('//time//text()').get().strip()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[contains(@class,"col-xs-12 col-xs-offset-0")]//text()[not (ancestor::li[@class="pdf"]) and not (ancestor::div[@class="row"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		if 'Допълнителна информация за медии:' in content[-7:]:
			content = content[:-7]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=UnicreditnewsItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()

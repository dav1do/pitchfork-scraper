# -*- coding: utf-8 -*-
import scrapy
from pitchfork.items import PitchforkListItem


class StaffListsAlbumsSpider(scrapy.Spider):
    name = "staff_lists_albums"
    allowed_domains = ["http://pitchfork.com", "pitchfork.com"]
    start_urls = [
        'http://pitchfork.com/features/staff-lists/9768-albums-of-the-year-2015-honorable-mention/',
        'http://pitchfork.com/features/staff-lists/9292-albums-of-the-year-honorable-mention/',
        'http://pitchfork.com/features/staff-lists/9559-albums-of-the-year-2014-honorable-mention/',
        'http://pitchfork.com/features/staff-lists/9558-the-50-best-albums-of-2014/',
        'http://pitchfork.com/features/staff-lists/9293-the-top-50-albums-of-2013/',
        'http://pitchfork.com/features/staff-lists/9764-the-50-best-albums-of-2015']
    custom_settings = {'FEED_EXPORT_FIELDS': ['rank', 'artist', 'album', 'label', 'year', 'review_text']}

    def parse(self, response):
        next_button_url = self.get_next_button(response)
        year = self.get_year(response)
        for album in response.xpath('//div[@class="text year-end-review"]'):
            item = PitchforkListItem()
            item['year'] = year
            item['artist'] = album.xpath('.//div[@class="title"]/h1/text()').extract()[0]
            item['album'] = album.xpath('.//div[@class="title"]/h2/text()').extract()[0]
            item['label'] = album.xpath('.//div[@class="title"]/h3/text()').extract()[0]
            try:
                item['rank'] = album.xpath('.//div[@class="rank"]/text()').extract()[0]
            except IndexError:
                pass  # rank isn't set for honorable mention pages
            review_text = album.xpath('.//div[@class="review-content"]//p/text()').extract()
            item['review_text'] = ''.join(review_text)
            yield item
        if next_button_url:
            yield scrapy.Request(next_button_url, callback=self.parse, meta={'year': year})

    def get_next_button(self, response):
        try:
            next_button = response.css('span.next-container > a.next::attr(href)').extract()[0]
            next_button_url = response.urljoin(next_button)
        except IndexError:
            next_button_url = None
        return next_button_url

    def get_year(self, response):
        try:
            year = response.xpath('//h1[@class="feature-title"]/text()').extract()[0]
        except IndexError:
            try:
                year = response.meta['year']
            except KeyError:
                year = 0
        return year

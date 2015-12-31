# -*- coding: utf-8 -*-
import scrapy
from pitchfork.items import PitchforkReviewItem
from pitchfork.pipelines import PitchforkReviewsPipeline
from datetime import datetime
from time import strptime
import logging


class ReviewsSpider(scrapy.Spider):
    name = "reviews"
    allowed_domains = ["pitchfork.com"]
    start_urls = ['http://pitchfork.com/reviews/albums/']

    def __init__(self, all_reviews=False, *args, **kwargs):
        scrapy.Spider.__init__(self, *args, **kwargs)
        self.all_reviews = all_reviews
        self.session = PitchforkReviewsPipeline()
        recent_review = self.session.get_most_recent_review()
        if recent_review:
            self.recent_album = recent_review.splash_album
            self.recent_artist = recent_review.splash_artist
            self.recent_date = recent_review.review_date
        elif not self.all_reviews:
            raise ValueError('Couldn\'t determine where to stop searching for reviews and not collecting all.')

    def parse(self, response):
        # find the next button before we navigate through each review on the page
        try:
            href = response.css('#main a.next::attr(href)')[0]
            next_page = response.urljoin(href.extract())
        except IndexError:  # if there's no Next link, we're hopefully on the last page
            next_page = None
        for album in response.css('#main > ul > li > ul > li'):
            splash_artist = album.xpath('.//div[@class="info"]/h1/text()').extract()[0]
            splash_album = album.xpath('.//div[@class="info"]/h2/text()').extract()[0]
            splash_date = album.xpath('.//div[@class="info"]/h4/text()').extract()[0]
            splash_date = self.make_datetime_from_date_string(splash_date, '%b %d, %Y')
            if self.stop_check(splash_artist, splash_album, splash_date):
                logging.info('Stop check passed -- quitting')
                raise StopIteration
            if self.session.album_in_database(splash_artist, splash_album, splash_date):
                # don't follow the link if we've already stored this review
                continue
            review_url = response.urljoin(album.css('a::attr(href)').extract()[0])
            yield scrapy.Request(review_url, callback=self.parse_album,
                                 meta={'album': splash_album, 'artist': splash_artist, 'review_date': splash_date})
        if not next_page:
            raise StopIteration
        yield scrapy.Request(next_page, callback=self.parse)

    def parse_album(self, response):
        info = response.xpath('//*[@id="main"]//div[@class="info"]')
        if response.xpath('//ul[@class="review-multi"]'):
            # see http://pitchfork.com/reviews/albums/21259-white-light-from-the-mouth-of-infinity-love-of-life/
                for review in info:
                    item = self.parse_review_details(response, review)
                    yield item
        else:
            yield self.parse_review_details(response, info)

    def parse_review_details(self, response, info):
        # specific method for details so we can call it twice for same review page
        item = PitchforkReviewItem()
        try:
            item['artist'] = info.xpath('.//h1/a/text()').extract()[0]
        except IndexError:  # there wasn't an <a> element means the artist doesn't have a page (e.g. Various Artists)
            item['artist'] = info.xpath('.//h1/text()').extract()[0]
        item['album'] = info.xpath('.//h2/text()').extract()[0]
        item['splash_artist'] = response.meta['artist']
        item['splash_album'] = response.meta['album']
        label_date = info.xpath('.//h3/text()').extract()
        label_date = label_date[0].strip().split('\n')  # not super resilient but should work
        item['label'] = label_date[0].strip()
        try:
            item['year'] = label_date[1].strip()
        except IndexError:
            # greatest hits don't have a year so let it go as null
            # see for example http://pitchfork.com/reviews/albums/2290-1s/
            pass
        item['reviewer'] = info.xpath('.//address/text()').extract()[0]
        # Ignore the review_date item on the review page since we get it from previous page
        # review_date = info.xpath('.//h4/span/text()').extract()[0]
        # item['review_date'] = self.make_datetime_from_date_string(review_date, '%B %d, %Y')
        item['review_date'] = response.meta['review_date']
        item['score'] = float(info.xpath('./span/text()').extract()[0].strip())
        # Best New Reissue or Best New Music
        item['accolades'] = info.xpath('./div[@class="bnm-label"]/text()').extract()[0].strip()
        text = response.xpath('//*[@id="main"]//div[@class="editorial"]/p/text()').extract()
        item['review_text'] = ''.join(text)
        item['review_url'] = response.url
        return item

    def stop_check(self, artist, album, date):
        """
        decide if we should stop searching. might be good to move if self.all_reviews above
        so we can avoid a function call but leaving it here because it encapsulates logic even
        though it's slower.
        @param artist: artist name, will be compared to the splash_artist in the DB
        @param album: album name, will be compared to splash_album in the DB
        @param date: date in datetime, will be compared to review_date in the DB
        @return: True if we should stop, False otherwise
        """
        if self.all_reviews:
            return False
        if artist == self.recent_artist and album == self.recent_album and self.recent_date == date:
            return True
        return False

    @staticmethod
    def make_datetime_from_date_string(date_string, format_string):
        """
        @param date_string: the date string to format
        @param format_string: format for time.strptime
        @return: a datetime object or datetime.min if it's an invalid format
        """
        try:
            date_string = strptime(date_string, format_string)
            date_string = datetime(*date_string[:6])  # magic unpacking of the struc_time object
        except ValueError:
            date_string = datetime.min
        return date_string

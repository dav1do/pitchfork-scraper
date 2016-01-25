# -*- coding: utf-8 -*-
import scrapy
from pitchfork.items import MetacriticItem
from pitchfork.pipelines import MetacriticReviewsPipeline
from datetime import datetime
from time import strptime
import logging


class MetacriticSpider(scrapy.Spider):
    name = 'metacritic'
    allowed_domains = ["metacritic.com"]
    start_urls = ['http://www.metacritic.com/browse/albums/release-date/available/date?view=condensed']
    custom_settings = {
        'METACRITICREVIEWSPIPELINE_ENABLED': True
    }

    def __init__(self, all_reviews=False, *args, **kwargs):
        scrapy.Spider.__init__(self, *args, **kwargs)
        self.all_reviews = all_reviews
        self.session = MetacriticReviewsPipeline()
        recent_review = self.session.get_most_recent_review()
        if recent_review:
            self.recent_album = recent_review.album
            self.recent_artist = recent_review.artist
            self.recent_date = recent_review.review_date
        elif not self.all_reviews:
            raise ValueError('Couldn\'t determine where to stop searching for reviews and not collecting all.')

    def parse(self, response):
        item = MetacriticItem()
        try:
            href = response.css('span.flipper.next > a::attr(href)').extract()[0]
            next_page = response.urljoin(href)
        except IndexError:  # if there's no Next link, we're hopefully on the last page
            next_page = None
        for album in response.css('#main ol > li > div.product_wrap'):
            try:
                item['album'] = album.xpath('./div[@class="basic_stat product_title"]/a/text()').extract()[0]
                item['album'] = item['album'].strip(' \n')
                item['critic_score'] = album.xpath(
                        './div[@class="basic_stat product_score brief_metascore"]/div/text()').extract()[0]
                stats = album.xpath('./div[@class="basic_stat condensed_stats"]')
                item['artist'] = stats.xpath('.//li[@class="stat product_artist"]/span/text()').extract()[1]
                item['user_score'] = stats.xpath('.//li[@class="stat product_avguserscore"]/span/text()').extract()[1]
                date_string = stats.xpath('.//li[@class="stat release_date full_release_date"]/span/text()')\
                    .extract()[1]
            except IndexError:
                # skip the review info if we don't get all the information
                continue
            try:
                item['review_date'] = strptime(date_string, '%b %d, %Y')
                item['year'] = item['review_date'].tm_year
                item['review_date'] = datetime(*item['review_date'][:6])  # magic unpacking of the struc_time object
            except ValueError:
                pass
            try:
                # critic score must be first since user_score may be 'tbd' if there aren't enough reviews
                item['critic_score'] = float(item['critic_score'])
                item['user_score'] = float(item['user_score'])
            except ValueError:
                del item['user_score']  # if it's 'tbd' put NaN in database
            if self.stop_check(item['artist'], item['album'], item['review_date']):
                logging.info('Stop check passed -- quitting')
                raise StopIteration
            if self.session.album_in_database(item['artist'], item['album'], item['review_date']):
                # TODO implement the update in the pipeline so we can replace 'tbd' values if they're new
                continue
            yield item
        if not next_page:
            raise StopIteration
        yield scrapy.Request(next_page, callback=self.parse)

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

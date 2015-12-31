# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class PitchforkReviewItem(Item):
    artist = Field()
    album = Field()
    review_text = Field()
    reviewer = Field()
    year = Field()
    review_date = Field()
    label = Field()
    score = Field()
    accolades = Field()
    review_url = Field()
    splash_artist = Field()
    splash_album = Field()


class PitchforkListItem(Item):
    artist = Field()
    album = Field()
    review_text = Field()
    rank = Field()
    year = Field()
    label = Field()

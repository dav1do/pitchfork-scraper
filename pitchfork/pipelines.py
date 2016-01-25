# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from models import Reviews, db_connect, create_tables, MetacriticReviews
from scrapy.exceptions import NotConfigured


class BasePipeline(object):

    def __init__(self):
        engine = db_connect()
        create_tables(engine)
        self.Session = sessionmaker(bind=engine)

    def add_item_to_database(self, db_item):
        session = self.Session()
        try:
            session.add(db_item)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


class PitchforkReviewsPipeline(BasePipeline):
    """
    Pitchfork pipeline for storing reviews in the database
    """

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('PITCHFORKREVIEWSPIPELINE_ENABLED'):
            # if this isn't specified in settings, the pipeline will be completely disabled
            raise NotConfigured
        return cls()

    def process_item(self, item, spider):
        review = Reviews(**item)
        self.add_item_to_database(review)
        return item

    def get_most_recent_review(self):
        session = self.Session()
        review = session.query(Reviews).order_by(Reviews.review_date.desc()).first()
        session.close()
        return review

    def album_in_database(self, artist, album, date):
        session = self.Session()
        # check the artist/album/date from the splash page
        # with the date we shouldn't skip duplicate reviews
        in_db = False
        if session.query(Reviews).filter(and_(Reviews.splash_album == album,
                                              Reviews.splash_artist == artist,
                                              Reviews.review_date == date)).count() > 0:
            in_db = True
        session.close()
        return in_db


class MetacriticReviewsPipeline(BasePipeline):
    """
    basically the same as pitchfork reviews pipeline but checks different database
    TODO make this OO with pitchfork pipeline
    """

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('METACRITICREVIEWSPIPELINE_ENABLED'):
            # if this isn't specified in settings, the pipeline will be completely disabled
            raise NotConfigured
        return cls()

    def process_item(self, item, spider):
        review = MetacriticReviews(**item)
        if self.album_in_database(item['artist'], item['album'], item['review_date']):
            self.update_database_record(review)
        else:
            self.add_item_to_database(review)
        return item

    def get_most_recent_review(self):
        session = self.Session()
        review = session.query(MetacriticReviews).order_by(MetacriticReviews.review_date.desc()).first()
        session.close()
        return review

    def album_in_database(self, artist, album, date):
        session = self.Session()
        in_db = False
        if session.query(MetacriticReviews).filter(and_(MetacriticReviews.album == album,
                                                        MetacriticReviews.artist == artist,
                                                        MetacriticReviews.review_date == date)).count() > 0:
            in_db = True
        session.close()
        return in_db

    def update_metacritic_record(self, db_item):
        # TODO implement this to update the 'tbd' values
        pass

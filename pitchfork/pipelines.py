# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from models import Reviews, db_connect, create_reviews_table
from scrapy.exceptions import DropItem


class PitchforkReviewsPipeline(object):
    """
    Pitchfork pipeline for storing reviews in the database
    """
    def __init__(self):
        engine = db_connect()
        create_reviews_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        review = Reviews(**item)
        try:
            session.add(review)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
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

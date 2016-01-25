from sqlalchemy import create_engine, Column, String, DateTime, Float, Integer, UniqueConstraint
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

import settings


def db_connect():
    """
    Connects to postgresql database
    @return: returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))


Base = declarative_base()


def create_tables(engine):
    Base.metadata.create_all(engine)


class Reviews(Base):
    """sqlalchemy pitchfork.com reviews model"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    album = Column('album', String)
    artist = Column('artist', String)
    review_date = Column('review_date', DateTime)
    score = Column('score', Float)
    # year is in inconsistent format from pitchfork so stick with string
    year = Column('year', String, nullable=True)
    label = Column('label', String, nullable=True)
    accolades = Column('accolades', String, nullable=True)
    review_text = Column('review_text', String, nullable=True)
    reviewer = Column('reviewer', String, nullable=True)
    splash_artist = Column('splash_artist', String)
    splash_album = Column('splash_album', String)
    review_url = Column('review_url', String)

    # enforce unique row with 'artist+album+review_date' unique constraint
    # this seems cleaner/simpler than a composite primary key
    __table_args__ = (
        UniqueConstraint('artist', 'album', 'review_date', name='_artist_album_review_date_uc'),
    )

    def __repr__(self):
        return "<Reviews(album='%s', artist='%s', score=%s, year=%s, review_date=%s" \
               "label=%s, accolades=%s, review_text=%s, reviewer=%s, splash_artist=%s" \
               "splash_album=%s, review_url=%s>" % (
                    self.album, self.artist, self.score, self.year, self.review_date,
                    self.label, self.accolades, self.review_text[:50], self.reviewer,
                    self.splash_artist, self.splash_album, self.review_url)


class MetacriticReviews(Base):
    """sqlalchemy metacritic.com music reviews model"""
    __tablename__ = "metacritic"

    id = Column(Integer, primary_key=True)
    album = Column('album', String)
    artist = Column('artist', String)
    review_date = Column('review_date', DateTime, nullable=True)
    year = Column('year', Integer, nullable=True)
    critic_score = Column('critic_score', Float)
    user_score = Column('user_score', Float, nullable=True)

    # enforce unique row with 'artist+album+review_date' unique constraint
    # this seems cleaner/simpler than a composite primary key
    __table_args__ = (
        UniqueConstraint('artist', 'album', 'review_date', name='_mc_artist_album_review_date_uc'),
    )

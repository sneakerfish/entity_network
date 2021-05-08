from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

news_item_entities = Table('news_items_entities', Base.metadata,
                           Column('entity_id', ForeignKey('entities.id'), primary_key=True),
                           Column('news_item_id', ForeignKey('news_items.id'), primary_key=True))

class Entity(Base):
    __tablename__ = 'entities'

    id = Column(Integer, primary_key=True)
    entity_name = Column(String)
    entity_type = Column(String)

    news_items = relationship('NewsItem', secondary=news_item_entities,
                              back_populates='entities')

    def __init__(self, ent_name, ent_type):
        self.entity_name = ent_name
        self.entity_type = ent_type

    def __repr__(self):
        print("<Entity: id: {}, name: {}, type: {}>".format(self.id, self.entity_name, self.entity_type))

class NewsItem(Base):
    __tablename__ = 'news_items'

    id = Column(Integer, primary_key=True)
    newstext = Column(String)
    url = Column(String)
    title = Column(String)
    authors = Column(String)
    processed = Column(Integer)

    entities = relationship('Entity', secondary=news_item_entities,
                            back_populates='news_items')

    def __init__(self, newstext, url, title, authors, processed):
        self.newstext = newstext
        self.url = url
        self.title = title
        self.authors = authors
        self.processed = processed

    def __repr__(self):
        print("<NewsItem: title {}, url: {}>".format(str(self.title)[:30], str(self.url)[:30]))

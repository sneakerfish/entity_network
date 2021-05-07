# In newer versions, this should be from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class Entity(Base):
    __tablename__ = 'entities'

    id = Column(Integer, primary_key=True)
    entity_name = Column(String)
    entity_type = Column(String)


class NewsItem(Base):
    __tablename__ = 'news_items'

    id = Column(Integer, primary_key=True)
    newstext = Column(String)
    authors = Column(String)
    url = Column(String)
    title = Column(String)
    processed = Column(Integer)

class NewsItemEntity(Base):
    __tablename__ = 'news_items_entities'

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entities.id'))
    news_item_id = Column(Integer, ForeignKey('news_items.id'))

    entity = relationship("entity", back_populates="entities")
    news_item = relationship("news_item", back_populates="news_items")

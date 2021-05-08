import sqlalchemy, json, spacy, random, glob, re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Entity, NewsItem
from neomodel import StructuredNode, StringProperty, Relationship, RelationshipTo, RelationshipFrom, config


db_string = "postgresql://postgres:postgres@localhost:5432/news"
engine = create_engine(db_string)
Session = sessionmaker(bind=engine)
session = Session()

config.DATABASE_URL = "neo4j://neo4j:inq6mth@localhost:7687"

class PersonEntity(StructuredNode):
    entity_name = StringProperty(unique_index=True)

class GeoEntity(StructuredNode):
    entity_name = StringProperty(unique_index=True)

class OrgEntity(StructuredNode):
    entity_name = StringProperty(unique_index=True)

class ArtEntity(StructuredNode):
    entity_name = StringProperty(unique_index=True)

class ProdEntity(StructuredNode):
    entity_name = StringProperty(unique_index=True)

class NewsItemNode(StructuredNode):
    url = StringProperty(unique_index=True)
    title = StringProperty()
    people = Relationship('PersonEntity', 'RELATED_TO')
    places = Relationship('GeoEntity', 'RELATED_TO')
    orgs = Relationship('OrgEntity', 'RELATED_TO')
    artworks = Relationship('ArtEntity', 'RELATED_TO')
    products = Relationship('ProdEntity', 'RELATED_TO')

def add_entities(session):
    for entity in session.query(Entity):
        if entity.entity_type == "PERSON":
            graph_entity = PersonEntity(entity_name=entity.entity_name).save()
        elif entity.entity_type == "ORG":
            graph_entity = OrgEntity(entity_name=entity.entity_name).save()
        elif entity.entity_type == "PRODUCT":
            graph_entity = ProdEntity(entity_name=entity.entity_name).save()
        elif entity.entity_type == "WORK_OF_ART":
            graph_entity = ArtEntity(entity_name=entity.entity_name).save()
        else:
            graph_entity = GeoEntity(entity_name=entity.entity_name).save()

def add_news_items(session):
    for item in session.query(NewsItem):
        news_item = NewsItemNode(url=item.url,
                                 title=item.title[0:50]).save()
        for entity in item.entities:
            if entity.entity_type == "PERSON":
                person = PersonEntity.nodes.filter(entity_name=entity.entity_name)[0]
                news_item.people.connect(person)
            elif entity.entity_type == "ORG":
                org = OrgEntity.nodes.filter(entity_name=entity.entity_name)[0]
                news_item.orgs.connect(org)
            elif entity.entity_type == "PRODUCT":
                product = ProdEntity.nodes.filter(entity_name=entity.entity_name)[0]
                news_item.products.connect(product)
            elif entity.entity_type == "WORK_OF_ART":
                artwork = ArtEntity.nodes.filter(entity_name=entity.entity_name)[0]
                news_item.artworks.connect(artwork)
            else:
                place = GeoEntity.nodes.filter(entity_name=entity.entity_name)[0]
                news_item.places.connect(place)

if __name__ == "__main__":
    add_entities(session)
    add_news_items(session)

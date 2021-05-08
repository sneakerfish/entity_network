import sqlalchemy, json, spacy, random, glob, re
from fuzzywuzzy import fuzz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Entity, NewsItem

db_string = "postgresql://postgres:postgres@localhost:5432/news"
engine = create_engine(db_string)
Session = sessionmaker(bind=engine)
session = Session()

nlp = spacy.load("en_core_web_lg")

def find_entities(text):
    doc = nlp(text)
    entities = {(str(t.text), t.label_) for t in doc.ents if t.label_ in ["ORG", "PRODUCT", "PERSON", "WORK_OF_ART", "GPE"]}
    people = list({item for item in entities if item[1] == "PERSON"})
    nonpeople = list({item for item in entities if item[1] != "PERSON"})

    # Try and reduce the number of people by combining shorter with longer for PERSON type.
    # This is because frequently, in a news story, only the first occurrence will have the whole
    # name.  Use fuzzywuzzy partial match for this.
    for i in range(len(people)):
        for j in range(len(people)):
            if j > len(people)-1 or i > len(people)-1:
                break
            if i == j:
                continue
            if len(people[i][0]) > len(people[j][0]) and fuzz.partial_ratio(people[i][0], people[j][0]) > 90:
                del people[j]
    return people + nonpeople

def check_url(url, session):
    """Check to see if we have alread added this URL.  Return True or False."""
    item = session.query(NewsItem).filter_by(url=url[0:500]).first()
    return item != None

def find_entity(entity_name, entity_type, session):
    entity = session.query(Entity).filter_by(entity_name=entity_name, entity_type=entity_type).first()
    return entity

def process_news_file(filename, session):
    with open(filename) as json_file:
        data = json.load(json_file)
    if not(data['url']) or check_url(data['url'], session):
        return False
    print(data['url'])
    entities = find_entities(data['text'])
    sp_pat = re.compile("\s+")
    news_item = NewsItem(newstext=sp_pat.sub(" ",data['text']),
                         url=data['url'][0:500],
                         title=data['title'],
                         authors=data['authors'], processed=1)
    session.add(news_item)

    for entity in entities:
        database_entity = find_entity(entity[0], entity[1], session)
        if database_entity == None:
            database_entity = Entity(entity[0], entity[1])
        news_item.entities.append(database_entity)
    session.commit()
    return entities

if __name__ == "__main__":
    filelist = glob.glob("rawdata/*/*.json")
    for file in filelist:
        process_news_file(file, session)

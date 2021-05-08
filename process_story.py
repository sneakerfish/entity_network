import sqlalchemy, json, spacy
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
    print("text is: {}".format(text))
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
            print ("comparing {} to {}".format(people[i][0], people[j][0]))
            if i == j:
                continue
            if len(people[i][0]) > len(people[j][0]) and fuzz.partial_ratio(people[i][0], people[j][0]) > 90:
                print("Deleting {}".format(people[j]))
                del people[j]
    return people + nonpeople

def process_news_file(filename, session):
    with open(filename) as json_file:
        data = json.load(json_file)
    entities = find_entities(data['text'])
    sp_pat = re.compile("\s+")
    news_item = NewsItem(newstext=sp_pat.sub(" ",data['text']),
                         url=data['url'],
                         title=data['title'],
                         authors=data['authors'], processed=1)
    session.add(news_item)
    for entity in entities:
        news_item.entities.append(Entity(entity[0], entity[1]))
    session.commit()
    return entities

if __name__ == "__main__":
    process_news_file("rawdata/cnn.com/47a4b4fb-a2e3-46d8-88e8-87f18ae34faa.json", session)

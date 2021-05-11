import sqlalchemy, json, spacy, random, glob, re
from fuzzywuzzy import fuzz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Entity, NewsItem
import pandas as pd

db_string = "postgresql://postgres:postgres@localhost:5432/news"
engine = create_engine(db_string)
Session = sessionmaker(bind=engine)
session = Session()

nlp = spacy.load("en_core_web_lg")

def geo_replace_abbreviation(entity):
    # Look up entity in a list of abbreviations of US states (obtained
    # from a USPS website).  In articles both the two character
    # abbreviation and the 1960s multiple-letter abbreviations are
    # used.
    state_abbr = pd.read_csv("state_abbr.csv")
    abbrev = {}
    for i in range(len(state_abbr)):
        abbrev[state_abbr.iloc[i, 5]] = state_abbr.iloc[i, 0]
        abbrev[state_abbr.iloc[i, 3]] = state_abbr.iloc[i, 0]
    # I found multiple representations of the United States.  Try
    # to standardize them here.
    abbrev["the United States"] = "United States"
    abbrev["The United States"] = "United States"
    abbrev["U.S"] = "United States"
    abbrev["U.S."] = "United States"
    abbrev["US"] = "United States"
    abbrev["us"] = "United States"
    abbrev["USA"] = "United States"
    abbrev["U.S.A."] = "United States"
    abbrev["united states"] = "United States"
    abbrev["America"] = "United States"
    abbrev["the US"] = "United States"
    abbrev["People's Republic of China"] = "China"
    abbrev["South Korea"] = "Korea"
    abbrev["BC"] = "British Columbia"
    abbrev["EU"] = "European Union"
    abbrev["E.U."] = "European Union"
    abbrev["GDR"] = "Germany"

    # Use a helper function to avoid reading the file multiple times.
    def helper(x):
        if x[0] in abbrev:
            return (abbrev[x[0]], x[1])
        else:
            return x
    return helper(entity)


def find_entities(text):
    # Process the given text using Spacy Large English model (en_core_web_lg).  Extract the unique
    # entities from the processed Spacy version of the text.  Separate entities in to people, places
    # and other entities.  For people, articles often mention the full name the first time a subject
    # is mentioned and then just the last name or an article and the last name thereafter.  Make
    # an attempt to reconcile this.  For Geographic entities, expand abbreviations for US and US
    # States.  More could probably be done here depending on the specifics of the corpus.
    doc = nlp(text)
    entities = {(str(t.text), t.label_) for t in doc.ents if t.label_ in ["ORG", "PRODUCT", "PERSON", "WORK_OF_ART", "GPE"]}
    people = list({item for item in entities if item[1] == "PERSON"})
    places = list({item for item in entities if item[1] == "GPE"})
    other_ents = list({item for item in entities if item[1] not in ["PERSON", "GPE"]})

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
    # Reduce the number of places by replacing abbreviations.
    places = list({geo_replace_abbreviation(ent) for ent in places})
    return people + places + other_ents

def check_url(url, session):
    """Check to see if we have alread added this URL.  Return True or False."""
    item = session.query(NewsItem).filter_by(url=url[0:500]).first()
    return item != None

def find_entity(entity_name, entity_type, session):
    """Find the given entity name and type if they exist.  Return None, otherwise."""
    entity = session.query(Entity).filter_by(entity_name=entity_name, entity_type=entity_type).first()
    return entity

def process_news_file(filename, session):
    # Process a single JSON news file.  The JSON is expected to have the following attributes:
    #   url - the URL for the story; it will be shortened to 500 characters to fit in the database.
    #   text - the full text of the article.  Sometimes, the Python Newspaper library is unable to
    #       fetch the text; in that case, do not add it to the database.
    #  authors - a list of authors if it was able to be extracted by the Newspaper library.
    #  title - The title of the article.  This will be shown in the Neo4J database.
    # All fields will be saved to the Postgres database.  If the "text" field is empty, the story
    # is not saved.
    with open(filename) as json_file:
        data = json.load(json_file)
    if not(data['url']) or check_url(data['url'], session) or data['text']=="":
        return False

    # Print out the URL so the user can see something
    print(data['url'])
    entities = find_entities(data['text'])
    sp_pat = re.compile("\\s+")
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

# Entity Network

This project attempts to do several things.  It will build a corpus of
news articles from various sources.  Every time you call the
`collect_data.py` program, it will go to the home page of several
national news sites and get a list of articles URLs.  Then, it will
get a sample of the URLs and check to see whether it has already
downloaded each URL.  If not, it will download the content and save it
to a JSON file in the `rawdata` directory.

A second program, called `process_story.py` will process all of the
stories.  Like `collect.data.py`, `process_story` will only fetch
stories that it has not seen before and will discard stories with an
empty story `text` as judged by the tool `newspaper`.  After fetching
the stories, it will store all of them in a Postgres database (called
`news`).  The `process_story.py` program will use the large English
model of Spacy to recognize Named Entities.

The Entities will be stored in an `entities` table related to the `news_items`
table through a third (join) table called `news_items_entities`.  The
`process_story.py` program will also use some state abbreviations and abbreviations
to the US to reduce the list of geographic entities.  It will use partial
matching to reduce the list of people entities.

Finally, a third program, called `process_graph.py` will create the
Neo4J graph of the story and entity database.

The Neo4J server as well as the Postgres server work through Docker.  You can
bring up both servers with the command: `docker-compose up`  You'll get an error
if you have a server running aready on ports 5432 (Postgres) or 7474 (Neo4J)
on the machine where you run this.  Also, I am running Python through a virtual
environment outside the Docker instance.

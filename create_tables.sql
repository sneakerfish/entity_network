drop table if exists entities;
create table entities (
    id serial,
    entity_name varchar(200),
    entity_type varchar(20)
    );
create unique index name_type_index on entities (entity_name, entity_type);

drop table if exists news_items;
create table news_items (
    id serial,
    newstext text,
    authors text,
    url varchar(500) unique,
    title text,
    processed smallint
    );
create unique index url_index on news_items (url);

drop table if exists news_items_entities;
create table news_items_entities (
    id serial,
    entity_id int,
    news_item_id int
    );
create unique index entity_news_index on news_items_entities (entity_id, news_item_id);

# process_data.py
# intended to be submitted via pyspark but produce results on the command line.

import os, spacy, en_core_web_lg
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, LongType, ArrayType
from pyspark.sql.functions import expr, col, column, udf, monotonically_increasing_id, trim, regexp_replace, explode

spark = SparkSession.builder.appName("process_data").getOrCreate()

nlp = spacy.load("en_core_web_lg")

def get_entities_udf():
    def get_entities(text):
        global nlp
        retlist = {}
        try:
            doc = nlp(text)
        except:
            nlp = spacy.load('en_core_web_lg')
            doc = nlp(text)
        retlist = {"{}:{}".format(t.text, t.label_) for t in doc.ents if t.label_ in ["ORG", "PRODUCT", "PERSON", "WORK_OF_ART", "GPE"]}
        return list(retlist)
    res_udf = udf(get_entities, ArrayType(StringType()))
    return res_udf


news_schema = schema = StructType([
    StructField("text", StringType(), False),
    StructField("title", StringType(), False),
    StructField("authors", ArrayType(StringType()), False),
    StructField("url", StringType(), False)
])


df1 = spark.read.schema(news_schema).json("rawdata/cnn.com")
df2 = df1.withColumn("entities", get_entities_udf()(df1.text))
df2.printSchema()

# news = df2.withColumn("newtext", regexp_replace(col("text"), r'(\s+)', " "))

# news.write.jdbc("jdbc:postgresql:news", "news_items",
#                properties={"user": "postgres", "password": "postgres"})

entities = df2.select(explode("entities").alias("entity")).distinct()

entities.write.jdbc("jdbc:postgresql:news", "entity_temp",
                    properties={"user": "postgres", "password": "postgres"})

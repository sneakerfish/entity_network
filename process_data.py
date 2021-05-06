# process_data.py
# intended to be submitted via pyspark but produce results on the command line.

import os, spacy, en_core_web_lg
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, LongType, ArrayType
from pyspark.sql.functions import expr, col, column, udf

spark = SparkSession.builder.appName("process_data").getOrCreate()

nlp = spacy.load("en_core_web_lg")

def get_entities_udf():
    def get_entities(text):
        global nlp
        try:
            doc = nlp(text)
        except:
            nlp = spacy.load('en_core_web_lg')
            doc = nlp(text)
        return [t.text for t in doc.ents if t.label_ in ["ORG", "PRODUCT", "PERSON", "WORK_OF_ART", "GPE"]]
    res_udf = udf(get_entities, ArrayType(StringType()))
    return res_udf


news_schema = schema = StructType([
    StructField("text", StringType(), False),
    StructField("title", StringType(), False),
    StructField("authors", StringType(), False),
    StructField("url", StringType(), False)
    ])


df1 = spark.read.schema(news_schema).json("rawdata/cnn.com")
df2 = df1.withColumn("entities", get_entities_udf()(df1.text))
print(df2.take(1))


# df2.printSchema()
# df2.show()

print(entities("This is a test of Mr Spock goes to Washington in February, 2002."))

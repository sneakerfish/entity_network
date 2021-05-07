# process_data.py
# intended to be submitted via pyspark but produce results on the command line.

import os, spacy, en_core_web_lg
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, LongType, ArrayType
from pyspark.sql.functions import expr, col, column, udf, monotonically_increasing_id

spark = SparkSession.builder.appName("process_data").getOrCreate()

entities = spark.read.jdbc("jdbc:postgresql:news", "entities",
                           properties={"user": "postgres", "password": "postgres"})

entities.show()

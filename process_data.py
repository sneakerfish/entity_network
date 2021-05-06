# problem2.py
# intended to be submitted via pyspark but produce results on the command line.

from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, LongType
from pyspark.sql.functions import expr, col, column

spark = SparkSession.builder.appName("process_data").getOrCreate()

news_schema = schema = StructType([
    StructField("text", StringType(), False),
    StructField("title", StringType(), False),
    StructField("authors", StringType(), False),
    StructField("url", StringType(), False)
    ])
df1 = spark.read.schema(news_schema).json("rawdata/cnn.com")
df1.printSchema()
df1.show()

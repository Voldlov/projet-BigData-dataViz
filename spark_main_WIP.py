# Not tested

import re
import os
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, StructType, StructField, TimestampType, DoubleType, ArrayType
from pyspark.sql.functions import from_json, udf, col, array_contains, split, count
from pyspark.sql import functions as F
from pymongo import MongoClient

from tools import get_list_of_keys


def load_df_from_kafka(spark_s, topic):
    return spark_s \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "broker:29092") \
        .option("subscribe", topic) \
        .load()


# Return matching hashtags in a tweet text based on the config file
def get_matching_hashtags(tweet: str) -> list:
    hashtags = re.findall('([#][a-zA-Z]+)', str(tweet))
    return [item for item in CURRENCIES if '#{}'.format(item) in (tag.lower() for tag in hashtags)]


def write_row_in_tweet_mongo(df, id):
    df.write.format("mongo").mode("append").option("uri",
                                                   MONGODB_ATLAS_URI + "development.tweets" + "?retryWrites=true&w=majority").save()
    pass


def write_row_in_crypto_mongo(df, id):
    df.write.format("mongo").mode("append").option("uri",
                                                   MONGODB_ATLAS_URI + "development.cryptos" + "?retryWrites=true&w=majority").save()
    pass


def generate_result(df_to_treat, db, crypto):
    data = {
        "nbr_tweets": df_to_treat.count(),
        "crypto_name": crypto,
        "datetime": datetime.now() + timedelta(hours=1)
    }
    db['results'].insert_one(data)


# Transforme string array into an array
# Because of a previous error with another udf function returnType
@udf(returnType=ArrayType(StringType()))
def clean_crypto_array(value):
    return value.strip('[]').split(',')


CURRENCIES = get_list_of_keys('symbol')

load_dotenv()
MONGODB_ATLAS_USER = os.getenv("MONGODB_ATLAS_USER")
MONGODB_ATLAS_PASSWORD = os.getenv("MONGODB_ATLAS_PASSWORD")
MONGODB_ATLAS_URI = "mongodb+srv://{}:{}@cluster0.6jprsq1.mongodb.net/".format(MONGODB_ATLAS_USER,
                                                                               MONGODB_ATLAS_PASSWORD)
MONGO_DB_NAME = os.getenv("MONGODB_ATLAS_DATABASE")

pymongo_client = MongoClient(MONGODB_ATLAS_URI)

spark = SparkSession. \
    builder. \
    appName("pyspark-notebook"). \
    master("spark://spark-master:7077"). \
    config("spark.executor.memory", "2g"). \
    config("spark.mongodb.input.uri", MONGODB_ATLAS_URI). \
    config("spark.mongodb.output.uri", MONGODB_ATLAS_URI). \
    config("spark.jars.packages",
           "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0"). \
    getOrCreate()

# Get tweet stream the cast the data to a spark dataframe
tweet_stream_df = load_df_from_kafka(spark, "tweeting")
tweet_schema = StructType([StructField("text", StringType(), True), StructField('date', TimestampType(), True)])
tweets_values = tweet_stream_df.select(from_json(tweet_stream_df.value.cast("string"), tweet_schema).alias("tweet"))

df1 = tweets_values.select("tweet.*")
clean_tweets = F.udf(get_matching_hashtags, StringType())
raw_tweets = df1.withColumn('cryptos', clean_tweets(col("text")))

raw_tweets \
    .writeStream \
    .foreachBatch(write_row_in_tweet_mongo) \
    .start()


# Get crypto stream the cast the data to a spark dataframe
crypto_stream_df = load_df_from_kafka(spark, "crypto")
crypto_schema = StructType([StructField("name", StringType(), True), StructField("symbol", StringType(), True),
                            StructField("value", DoubleType(), True), StructField('date', TimestampType(), True)])
crypto_values = crypto_stream_df.select(from_json(crypto_stream_df.value.cast("string"), crypto_schema).alias("crypto"))
df_crypto = crypto_values.select("crypto.*")

df_crypto \
    .writeStream \
    .foreachBatch(write_row_in_crypto_mongo) \
    .start()

db = pymongo_client[MONGO_DB_NAME]

time_between_treatment = 900
while True:
    db["tweets"].drop()
    time.sleep(time_between_treatment)
    tweets_df = spark.read.format("mongo").option("uri", MONGODB_ATLAS_URI + "development.tweets").load()
    df = tweets_df.withColumn('crypto_array', clean_crypto_array("cryptos")).drop("cryptos")
    for crypto in CURRENCIES:
        generate_result(df.where(array_contains(df['crypto_array'], crypto)), db, crypto)

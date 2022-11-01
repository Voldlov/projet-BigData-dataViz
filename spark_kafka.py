from pyspark.sql import SparkSession
import os

# spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0 spark_kafka.py
#sans se connecter au cluster
#spark = SparkSession.builder.getOrCreate()

spark = SparkSession. \
    builder. \
    appName("pyspark-notebook"). \
    master("spark://spark-master:7077"). \
    config("spark.executor.memory", "2g"). \
    getOrCreate()

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "quickstart") \
    .load()
df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

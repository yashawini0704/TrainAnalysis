from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StringType

# 🔧 Kafka Config
KAFKA_BROKER = "34.29.73.57:9092"  # Your Kafka VM internal IP
TOPIC = "input-1"

# 🚀 Spark Session
spark = SparkSession.builder \
    .appName("TrainStationCongestionConsumer") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 📦 Define schema for JSON values from Kafka
schema = StructType() \
    .add("station_code", StringType()) \
    .add("train_no", StringType()) \
    .add("train_name", StringType()) \
    .add("arrival", StringType()) \
    .add("departure", StringType())

# 🔄 Read streaming data from Kafka
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()

# 🧹 Parse JSON
parsed_df = raw_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", schema).alias("data")) \
    .select("data.*")

# 🕐 Simulate actual arrival time (you can improve this later)
df = parsed_df.withColumn("event_time", current_timestamp())

# 🪟 20-minute rolling window, update every 5 min
windowed_counts = df \
    .withWatermark("event_time", "30 minutes") \
    .groupBy(
        window("event_time", "20 minutes", "5 minutes"),
        col("station_code")
    ) \
    .count() \    
    .withColumnRenamed("count", "train_count")

# 🚨 Add congestion alerts (more than 5 trains)
alerts = windowed_counts.withColumn(
    "congestion_alert",
    when(col("train_count") > 5, "🚨 Congested Train Station").otherwise("")
)

# 🖨️ Print output to console
query = alerts.writeStream \
    .outputMode("update") \
    .format("console") \
    .option("truncate", False) \
    .option("numRows", 50) \
    .start()

query.awaitTermination()

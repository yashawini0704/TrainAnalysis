from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import time
from kafka import KafkaProducer
import json

# 🔧 CONFIGURATION
KAFKA_BROKER = "34.29.73.57:9092"  # Your Kafka VM internal IP
TOPIC = "input-1"
CSV_FILE = "./Train_details_22122017.csv"  # ✅ Your file is in current directory

# 🚀 Spark Session
spark = SparkSession.builder \
    .appName("TrainCSVToKafkaStreamer") \
    .getOrCreate()

# 🛠️ Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 📥 Load CSV
df = spark.read.option("header", True).csv(CSV_FILE)

# 🧹 Clean + Standardize Columns
df = df.select(
    col("Station Code").alias("station_code"),
    col("Train No").cast("string").alias("train_no"),
    col("Train Name").alias("train_name"),
    col("Arrival time").alias("arrival"),
    col("Departure Time").alias("departure")
).na.drop(subset=["station_code", "arrival", "departure"])

print(f"✅ Cleaned rows: {df.count()}")

# 📨 Stream each row to Kafka
for row in df.collect():
    msg = {
        "station_code": row["station_code"],
        "train_no": row["train_no"],
        "train_name": row["train_name"],
        "arrival": row["arrival"],
        "departure": row["departure"]
    }
    producer.send(TOPIC, msg)
    producer.flush()
    print("✅ Sent:", msg)
    time.sleep(1)  # simulate live feed

import os
import json
from google.cloud import pubsub_v1

# 📍 CONFIG
PROJECT_ID = "data-mind-448014-b3"
TOPIC_ID = "congestion-alerts"
FOLDER_PATH = "/home/yashawini0704/congestion_alerts_output"

# 🚀 Pub/Sub Publisher Setup
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

# 📤 Publish valid JSON lines from all files
for filename in sorted(os.listdir(FOLDER_PATH)):
    filepath = os.path.join(FOLDER_PATH, filename)

    # ✅ Skip directories like _spark_metadata and others
    if not os.path.isfile(filepath) or filename.startswith(".") or filename.startswith("_"):
        continue

    if os.path.getsize(filepath) == 0:
        print(f"⚠️ Skipping empty file: {filename}")
        continue

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)  # Ensure it's valid JSON
                future = publisher.publish(topic_path, data=line.encode("utf-8"))
                print("✅ Published:", line)
            except Exception as e:
                print("❌ Error:", e)

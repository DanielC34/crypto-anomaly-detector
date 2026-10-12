
import requests
from kafka import KafkaProducer
import json
import time

# Connect to Kafka once and keep the connection open.
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

url = "https://api.coingecko.com/api/v3/simple/price"

params = {
    "ids": "bitcoin,ethereum,solana",
    "vs_currencies": "usd"
}

try:
    while True:
        try:
            # Fetch the latest crypto prices.
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            # Package the prices into an event.
            event = {
                "source": "coingecko",
                "data": data
            }

            # Send the event to Kafka.
            producer.send("crypto-prices", value=event)
            producer.flush()

            print("Sent:", event)

        except requests.RequestException as error:
            print("Price fetch failed:", error)

        # Wait 60 seconds before the next fetch.
        time.sleep(60)

except KeyboardInterrupt:
    print("Producer stopped.")

finally:
    producer.close()

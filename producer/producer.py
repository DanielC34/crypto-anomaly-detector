import requests
from kafka import KafkaProducer
import json

# Simple producer script: fetch crypto prices and publish to Kafka.
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

url = "https://api.coingecko.com/api/v3/simple/price"

params = {
    "ids": "bitcoin,ethereum,solana",
    "vs_currencies": "usd"
}

# Fetch latest prices from CoinGecko
response = requests.get(url, params=params)
data = response.json()

# Wrap the API response into a simple event with a source field
event = {
    "source": "coingecko",
    "data": data
}

# Send the event to the 'crypto-prices' Kafka topic
producer.send("crypto-prices", value=event)

# Flush pending messages and close the producer cleanly
producer.flush()
producer.close()

print("Sent:", event)
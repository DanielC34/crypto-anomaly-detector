
import json
from kafka import KafkaConsumer

from storage import (
    initialize_database,
    save_anomaly,
    save_price_observation,
)

THRESHOLD_PERCENT = 2.0

# Remember the most recent price for each cryptocurrency.
previous_prices = {}

# Ensure the database and its tables exist before processing messages.
initialize_database()

consumer = KafkaConsumer(
    "crypto-prices",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",
    group_id="crypto-anomaly-detector",
    value_deserializer=lambda message: json.loads(message.decode("utf-8")),
)

print("Monitoring crypto prices... Press Ctrl+C to stop.")

try:
    for message in consumer:
        event = message.value
        prices = event.get("data", {})

        for coin, currencies in prices.items():
            new_price = currencies.get("usd")

            if (
                not isinstance(new_price, (int, float))
                or isinstance(new_price, bool)
                or new_price <= 0
            ):
                continue

            previous_price = previous_prices.get(coin)
            change_percent = None

            if previous_price is None:
                print(f"Baseline set: {coin} = ${new_price:,.2f}")
            else:
                change_percent = (
                    (new_price - previous_price) / previous_price
                ) * 100

                if abs(change_percent) > THRESHOLD_PERCENT:
                    print(
                        f"ANOMALY: {coin} changed by "
                        f"{change_percent:+.2f}% "
                        f"(${previous_price:,.2f} -> ${new_price:,.2f})"
                    )

                    save_anomaly(
                        coin,
                        previous_price,
                        new_price,
                        change_percent,
                        THRESHOLD_PERCENT,
                    )
                else:
                    print(
                        f"Normal: {coin} changed by "
                        f"{change_percent:+.2f}%"
                    )

            # Save every valid observation, including the first baseline.
            save_price_observation(coin, new_price, change_percent)

            # Update the baseline for the next observation.
            previous_prices[coin] = new_price

except KeyboardInterrupt:
    print("\nDetector stopped.")
finally:
    consumer.close()

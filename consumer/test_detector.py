
def calculate_change(previous_price, new_price):
    return ((new_price - previous_price) / previous_price) * 100


previous_price = 100_000
new_price = 97_000
threshold = 2.0

change = calculate_change(previous_price, new_price)

print(f"Price change: {change:+.2f}%")
print(f"Anomaly detected: {abs(change) > threshold}")

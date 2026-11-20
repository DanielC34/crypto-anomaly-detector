
THRESHOLD_PERCENT = 2.0


def calculate_change(previous_price, new_price):
    """Calculate percentage change between two positive prices."""

    if previous_price <= 0:
        raise ValueError("Previous price must be greater than zero")

    return ((new_price - previous_price) / previous_price) * 100



def is_anomaly(change_percent, threshold=THRESHOLD_PERCENT):
    """Determine whether a percentage change exceeds the threshold."""

    return abs(change_percent) > threshold

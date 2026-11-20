
from detector import calculate_change, is_anomaly
import pytest


def test_calculate_percentage_decrease():
    result = calculate_change(100_000, 97_000)

    assert result == -3.0

def test_calculate_percentage_increase():
    result = calculate_change(100_000, 103_000)

    assert result == 3.0

def test_calculate_no_price_change():
    result = calculate_change(100_000, 100_000)

    assert result == 0.0

def test_detects_price_increase_above_threshold():
    assert is_anomaly(3.0) is True

def test_detects_price_decrease_above_threshold():
    assert is_anomaly(-3.0) is True

def test_exact_negative_threshold_is_not_anomaly():
    assert is_anomaly(-2.0) is False

def test_exact_positive_threshold_is_not_anomaly():
    assert is_anomaly(2.0) is False

def test_small_price_increase_is_not_anomaly():
    assert is_anomaly(1.5) is False

def test_small_price_decrease_is_not_anomaly():
    assert is_anomaly(-1.5) is False

def test_zero_previous_price_raises_error():
    with pytest.raises(ValueError):
        calculate_change(0, 100)

def test_negative_previous_price_raises_error():
    with pytest.raises(ValueError):
        calculate_change(-100, 100)
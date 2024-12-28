"""
Tests for time_utils module
"""
from datetime import datetime
import pytest
from backend.utils.time_utils import iter_dates, timestamp_to_string


def test_iter_dates():
    """
    iter_dates function tester
    """
    start_date = "2024-12-01"
    end_date = "2024-12-05"
    expected = ["20241201", "20241202", "20241203", "20241204", "20241205"]
    assert iter_dates(start_date, end_date) == expected

    start_date = "2024-12-01"
    end_date = "2024-12-01"
    expected = ["20241201"]
    assert iter_dates(start_date, end_date) == expected

    start_date = "2024-12-05"
    end_date = "2024-12-01"
    expected = []
    assert iter_dates(start_date, end_date) == expected

    with pytest.raises(ValueError):
        iter_dates("2024/12/01", "2024/12/05")


def test_timestamp_to_string():
    """
    timestamp_to_string function tester
    """
    timestamp = 1735225375
    expected_time = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
    assert timestamp_to_string(timestamp) == expected_time

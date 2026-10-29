"""Lab 6 - Code (line) coverage tests for fuel_station.py.

Goal: execute every line of fuel_station.py at least once.
Each test below is chosen to reach a line the starter tests never touch.

Run:
    coverage run -m pytest CodeCoverageTest_PES1UG24AM286_fuel_station.py
    coverage report -m
"""
import pytest
from fuel_station import fuel_bill, pump_allowed, session_status


# ---------------- fuel_bill ----------------

def test_unknown_grade_raises():
    # line: raise ValueError("unknown fuel grade")
    with pytest.raises(ValueError, match="unknown fuel grade"):
        fuel_bill("kerosene", 10, "silver")


def test_negative_litres_raises():
    # line: raise ValueError("invalid litres")
    with pytest.raises(ValueError, match="invalid litres"):
        fuel_bill("regular", -1, "silver")


def test_within_covered_litres():
    # line: return 0
    assert fuel_bill("regular", 8, "silver") == 0


def test_premium_gold_bulk_purchase():
    # lines: covered += 5, rate = 105, rate - 6, rate -= 4, return extra * rate
    # covered = 15 + 5 = 20, extra = 40, rate = 105 - 6 - 4 = 95
    assert fuel_bill("premium", 60, "gold") == 40 * 95


def test_diesel_small_extra():
    # line: rate = 90
    # covered = 20, extra = 10, rate = 90
    assert fuel_bill("diesel", 30, "silver") == 10 * 90


# ---------------- pump_allowed ----------------

def test_fleet_request():
    # line: return litres_requested <= 200
    assert pump_allowed(150, 3, True) is True


def test_non_fleet_over_limit():
    # line: return False
    assert pump_allowed(70, 1, False) is False


def test_pump_allowed():
    # line: return containers <= 1
    assert pump_allowed(30, 1, False) is True


# ---------------- session_status ----------------

def test_card_payment_at_night_active():
    # lines: cutoff = 60, cutoff += 30, return "active"
    assert session_status(100, True, True) == "active"


def test_cash_warning():
    # lines: cutoff = 30, return "warning"
    assert session_status(20, False, False) == "warning"


def test_cash_timed_out():
    # line: return "timed_out"
    assert session_status(5, False, False) == "timed_out"

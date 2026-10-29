"""Lab 6 - Branch coverage tests for fuel_station.py.

Goal: make every decision in fuel_station.py evaluate to BOTH True and False,
and pin down the boundary values (==, <, <=, >) where the behaviour flips.

The code-coverage suite already ran every line, but it never took the
False side of `if loyalty_tier == "gold"` inside `if extra > 30`
(branch 21->23). The tests below close that gap and also cover every
other branch edge and boundary.

Run:
    coverage run --branch -m pytest BranchCoverageTest_PES1UG24AM286_fuel_station.py
    coverage report -m
"""
import pytest
from fuel_station import fuel_bill, pump_allowed, session_status


# ======================= fuel_bill =======================

# --- if grade not in VOUCHER_LITRES (True / False) ---
@pytest.mark.parametrize("grade", ["kerosene", "", "Regular", None])
def test_unknown_grade_raises(grade):
    with pytest.raises(ValueError, match="unknown fuel grade"):
        fuel_bill(grade, 10, "silver")


# --- if litres < 0 (True / False, boundary at 0) ---
def test_negative_litres_raises():
    with pytest.raises(ValueError, match="invalid litres"):
        fuel_bill("diesel", -0.5, "gold")


def test_zero_litres_is_valid_and_free():
    assert fuel_bill("regular", 0, "silver") == 0


# --- if loyalty_tier == "gold" and grade != "diesel" ---
# True: gold on regular/premium gets 5 extra covered litres
def test_gold_regular_gets_extra_covered_litres():
    # covered = 10 + 5 = 15 -> 15 litres is still free
    assert fuel_bill("regular", 15, "gold") == 0
    assert fuel_bill("regular", 16, "gold") == 1 * 105


# False (first operand False): non-gold customer
def test_silver_regular_no_extra_covered_litres():
    assert fuel_bill("regular", 15, "silver") == 5 * 105


# False (second operand False): gold customer buying diesel
def test_gold_diesel_does_not_extend_voucher():
    # covered stays 20, extra = 5, rate = 90
    assert fuel_bill("diesel", 25, "gold") == 5 * 90


# --- if extra <= 0 (True / False, boundary at 0) ---
@pytest.mark.parametrize("grade, litres, expected", [
    ("regular", 10, 0),          # extra == 0  -> free
    ("regular", 11, 1 * 105),    # extra == 1  -> charged
    ("premium", 15, 0),          # extra == 0
    ("diesel", 20, 0),           # extra == 0
    ("diesel", 21, 1 * 90),      # extra == 1
])
def test_extra_boundary(grade, litres, expected):
    assert fuel_bill(grade, litres, "silver") == expected


# --- if grade == "diesel" (True / False) ---
def test_diesel_rate():
    assert fuel_bill("diesel", 30, "silver") == 10 * 90


def test_petrol_rate():
    assert fuel_bill("premium", 25, "silver") == 10 * 105


# --- if extra > 30 (True / False, boundary at 30/31) ---
def test_extra_exactly_30_no_bulk_discount():
    # extra = 30 -> not > 30 -> full rate
    assert fuel_bill("regular", 40, "silver") == 30 * 105


def test_extra_31_gets_bulk_discount():
    # extra = 31 -> rate 105 - 6 = 99
    assert fuel_bill("regular", 41, "silver") == 31 * 99


# --- nested if loyalty_tier == "gold" inside extra > 30 (True / False) ---
def test_bulk_gold_petrol_extra_discount():
    # covered 20, extra 40, rate 105 - 6 - 4 = 95
    assert fuel_bill("premium", 60, "gold") == 40 * 95


def test_bulk_non_gold_petrol_no_extra_discount():
    # covered 15, extra 35, rate 105 - 6 = 99   (branch 21->23)
    assert fuel_bill("premium", 50, "silver") == 35 * 99


def test_bulk_gold_diesel_extra_discount():
    # covered 20 (no gold bonus), extra 40, rate 90 - 6 - 4 = 80
    assert fuel_bill("diesel", 60, "gold") == 40 * 80


def test_bulk_non_gold_diesel_no_extra_discount():
    # covered 20, extra 40, rate 90 - 6 = 84
    assert fuel_bill("diesel", 60, "silver") == 40 * 84


# ===================== pump_allowed =====================

# --- if is_fleet (True): limit 200, containers ignored ---
@pytest.mark.parametrize("litres, containers, expected", [
    (200, 0, True),    # boundary: exactly 200
    (201, 0, False),   # just over
    (100, 5, True),    # many containers do not matter for fleet
])
def test_fleet_limits(litres, containers, expected):
    assert pump_allowed(litres, containers, True) is expected


# --- is_fleet False -> if litres_requested > 60 (True / False) ---
def test_non_fleet_over_60_rejected():
    assert pump_allowed(61, 0, False) is False


def test_non_fleet_exactly_60_allowed():
    assert pump_allowed(60, 1, False) is True


# --- return containers <= 1 (True / False) ---
@pytest.mark.parametrize("containers, expected", [
    (0, True),
    (1, True),
    (2, False),
])
def test_non_fleet_container_limit(containers, expected):
    assert pump_allowed(30, containers, False) is expected


# ==================== session_status ====================
# cutoff: card 60 / cash 30, +30 at night
# active   : seconds_left >= cutoff
# warning  : cutoff - 15 <= seconds_left < cutoff
# timed_out: seconds_left <  cutoff - 15

@pytest.mark.parametrize("seconds, card, night, expected", [
    # card, day   (cutoff 60)
    (60, True, False, "active"),
    (59, True, False, "warning"),
    (45, True, False, "warning"),
    (44, True, False, "timed_out"),
    # card, night (cutoff 90)
    (90, True, True, "active"),
    (75, True, True, "warning"),
    (74, True, True, "timed_out"),
    # cash, day   (cutoff 30)
    (30, False, False, "active"),
    (15, False, False, "warning"),
    (14, False, False, "timed_out"),
    # cash, night (cutoff 60)
    (60, False, True, "active"),
    (45, False, True, "warning"),
    (44, False, True, "timed_out"),
])
def test_session_status_all_paths(seconds, card, night, expected):
    assert session_status(seconds, card, night) == expected


def test_session_zero_seconds_times_out():
    assert session_status(0, True, True) == "timed_out"

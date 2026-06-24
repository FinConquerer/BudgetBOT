from app.core.rules.calculators import (
    calculate_50_30_20_allocation,
    calculate_monthly_surplus,
    calculate_ratio,
    calculate_total_expenses,
)


def test_calculate_total_expenses():
    assert calculate_total_expenses(7_000_000, 5_000_000, 1_000_000) == 13_000_000


def test_calculate_monthly_surplus():
    assert calculate_monthly_surplus(20_000_000, 13_000_000) == 7_000_000


def test_calculate_ratio():
    assert calculate_ratio(4_000_000, 20_000_000) == 0.2


def test_calculate_50_30_20_allocation():
    allocation = calculate_50_30_20_allocation(20_000_000)
    assert allocation.needs == 10_000_000
    assert allocation.wants == 6_000_000
    assert allocation.savings == 4_000_000

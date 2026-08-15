"""Pillar XXXIII: Enterprise Value Creation — canonical research-layer reference."""

from __future__ import annotations

from pillars.xxxiii_enterprise_value import EnterpriseValueCreation


def compute_enterprise_value(fcf_forecast, wacc, terminal_growth=0.02):
    engine = EnterpriseValueCreation()
    return engine.enterprise_value(fcf_forecast, wacc, terminal_growth)


def check_value_creation(roic, wacc):
    engine = EnterpriseValueCreation()
    return engine.value_created(roic, wacc)


def compute_economic_profit(invested_capital, roic, wacc):
    engine = EnterpriseValueCreation()
    return engine.economic_profit(invested_capital, roic, wacc)

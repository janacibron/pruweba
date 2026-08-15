# PILLAR XXXIII: ENTERPRISE VALUE CREATION
from __future__ import annotations

try:
    from .base import BasePillar
except ImportError:
    from base import BasePillar


class EnterpriseValueCreation(BasePillar):
    name = "Enterprise Value Creation"
    domain = "Finance"
    mandate = (
        "Connect operations, finance, and strategy through a governed valuation "
        "model. Every enterprise decision is traceable to value creation or destruction."
    )

    def health_check(self) -> tuple[bool, str]:
        return True, f"{self.name} initialized"

    @staticmethod
    def enterprise_value(fcf_forecast, wacc, terminal_growth=0.02):
        ev = 0.0
        n = len(fcf_forecast)
        for t, fcf in enumerate(fcf_forecast, 1):
            pv = fcf / ((1 + wacc) ** t)
            ev += pv
        terminal_fcf = fcf_forecast[-1] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (wacc - terminal_growth)
        pv_terminal = terminal_value / ((1 + wacc) ** n)
        ev += pv_terminal
        return ev

    @staticmethod
    def value_created(roic, wacc):
        return roic > wacc

    @staticmethod
    def economic_profit(invested_capital, roic, wacc):
        return (roic - wacc) * invested_capital


print('[XXXIII] Enterprise Value Creation: ready')

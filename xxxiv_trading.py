# PILLAR XXXIV: MARKET TRADING & POSITION SIZING
from __future__ import annotations

try:
    from .base import BasePillar
except ImportError:
    from base import BasePillar


class MarketTrading(BasePillar):
    name = "Market Trading & Position Sizing"
    domain = "Trading"
    mandate = (
        "Govern the full trading stack: signal generation, position sizing, "
        "execution, risk management, and performance tracking. "
        "No trade leaves without verified sizing and risk bounds."
    )

    def health_check(self) -> tuple[bool, str]:
        return True, f"{self.name} initialized"

    @staticmethod
    def kelly_criterion(win_probability, win_loss_ratio):
        return (win_probability * win_loss_ratio - (1 - win_probability)) / win_loss_ratio

    @staticmethod
    def expected_value(win_prob, avg_win, loss_prob, avg_loss):
        return (win_prob * avg_win) - (loss_prob * avg_loss)

    @staticmethod
    def sharpe_ratio(returns, risk_free_rate=0.02):
        excess = sum(returns) / len(returns) - risk_free_rate if returns else 0
        vol = (sum((r - sum(returns)/len(returns))**2 for r in returns) / len(returns)) ** 0.5 if returns else 0
        return excess / vol if vol > 0 else 0

    @staticmethod
    def max_drawdown(equity_curve):
        peak = equity_curve[0]
        max_dd = 0.0
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd
        return max_dd

    @staticmethod
    def profit_factor(gross_profit, gross_loss):
        return gross_profit / abs(gross_loss) if gross_loss != 0 else float('inf')

    @staticmethod
    def position_size(capital, kelly_fraction, entry_price, stop_loss):
        risk_per_trade = capital * kelly_fraction
        risk_per_unit = abs(entry_price - stop_loss)
        return risk_per_trade / risk_per_unit if risk_per_unit > 0 else 0

    @staticmethod
    def expectancy(win_rate, avg_win, loss_rate, avg_loss):
        return (win_rate * avg_win) - (loss_rate * avg_loss)


print('[XXXIV] Market Trading & Position Sizing: ready')

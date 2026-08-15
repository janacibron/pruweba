"""Pillar XXXIV: Market Trading & Position Sizing — canonical research-layer reference."""

from __future__ import annotations

from pillars.xxxiv_trading import MarketTrading


def kelly_criterion(win_probability, win_loss_ratio):
    engine = MarketTrading()
    return engine.kelly_criterion(win_probability, win_loss_ratio)


def expected_value(win_prob, avg_win, loss_prob, avg_loss):
    engine = MarketTrading()
    return engine.expected_value(win_prob, avg_win, loss_prob, avg_loss)


def sharpe_ratio(returns, risk_free_rate=0.02):
    engine = MarketTrading()
    return engine.sharpe_ratio(returns, risk_free_rate)


def max_drawdown(equity_curve):
    engine = MarketTrading()
    return engine.max_drawdown(equity_curve)


def profit_factor(gross_profit, gross_loss):
    engine = MarketTrading()
    return engine.profit_factor(gross_profit, gross_loss)


def position_size(capital, kelly_fraction, entry_price, stop_loss):
    engine = MarketTrading()
    return engine.position_size(capital, kelly_fraction, entry_price, stop_loss)


def expectancy(win_rate, avg_win, loss_rate, avg_loss):
    engine = MarketTrading()
    return engine.expectancy(win_rate, avg_win, loss_rate, avg_loss)

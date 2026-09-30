"""Tests for BacktestEngine functionality."""

import pytest

from minibacktester.engine import BacktestEngine
from minibacktester.models import Candle, Signal
from minibacktester.strategy import Strategy


class ConstantSignalStrategy(Strategy):
    """Test strategy emitting a constant signal or sequence of signals."""

    def __init__(self, signals):
        self.signals = signals
        self.call_count = 0

    def next(self, candle: Candle, history):
        if self.call_count < len(self.signals):
            sig = self.signals[self.call_count]
            self.call_count += 1
            return sig
        return Signal.HOLD


def test_engine_empty_candles():
    """Test engine handling empty candle sequence."""
    engine = BacktestEngine(initial_capital=10000.0)
    strategy = ConstantSignalStrategy([])
    result = engine.run(strategy, [])

    assert result.equity_curve == [10000.0]
    assert len(result.trades) == 0
    assert result.metrics.final_equity == 10000.0


def test_engine_buy_and_hold():
    """Test buying on first candle and holding to the end."""
    candles = [
        Candle("2023-01-01T00:00:00", 100, 105, 95, 100, 1000),
        Candle("2023-01-01T01:00:00", 100, 115, 95, 110, 1000),
        Candle("2023-01-01T02:00:00", 110, 125, 105, 120, 1000),
    ]
    # Emits BUY, then HOLD, HOLD
    strategy = ConstantSignalStrategy([Signal.BUY, Signal.HOLD, Signal.HOLD])
    engine = BacktestEngine(initial_capital=10000.0)
    result = engine.run(strategy, candles)

    # Started with 10,000 cash, bought at 100 => 100 units
    # Final price = 120 => Final equity = 12,000
    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.entry_price == 100.0
    assert trade.exit_price == 120.0
    assert trade.pnl == 2000.0
    assert result.metrics.final_equity == 12000.0
    assert result.metrics.total_return == 0.20


def test_engine_commission():
    """Test commission impact on trade execution."""
    candles = [
        Candle("2023-01-01T00:00:00", 100, 105, 95, 100, 1000),
        Candle("2023-01-01T01:00:00", 100, 105, 95, 100, 1000),
    ]
    strategy = ConstantSignalStrategy([Signal.BUY, Signal.SELL])
    # 1% commission
    engine = BacktestEngine(initial_capital=10000.0, commission_pct=0.01)
    result = engine.run(strategy, candles)

    # Cash after buy = 10000 * (1 - 0.01) = 9900 => size = 9900 / 100 = 99 units
    # Cash after sell = (99 * 100) * (1 - 0.01) = 9900 * 0.99 = 9801
    assert pytest.approx(result.metrics.final_equity, rel=1e-3) == 9801.0

"""Tests for SMA Crossover Strategy and strategy interface."""

import pytest

from minibacktester.models import Candle, Signal
from minibacktester.strategies.sma_crossover import SMACrossoverStrategy


def test_sma_crossover_invalid_windows():
    """Test parameter validation for fast and slow windows."""
    with pytest.raises(ValueError, match="fast_window must be at least 1"):
        SMACrossoverStrategy(fast_window=0, slow_window=10)

    with pytest.raises(ValueError, match="slow_window must be greater than fast_window"):
        SMACrossoverStrategy(fast_window=10, slow_window=10)

    with pytest.raises(ValueError, match="slow_window must be greater than fast_window"):
        SMACrossoverStrategy(fast_window=10, slow_window=5)


def test_sma_crossover_insufficient_history(simple_flat_candles):
    """Test HOLD signal when history length is less than slow_window + 1."""
    strategy = SMACrossoverStrategy(fast_window=3, slow_window=10)
    # 10 candles -> not enough history for slow_window(10) + 1 = 11
    short_history = simple_flat_candles[:10]

    signal = strategy.next(short_history[-1], short_history)
    assert signal == Signal.HOLD


def test_sma_crossover_buy_and_sell_signals():
    """Test golden cross (BUY) and death cross (SELL) signal generation."""
    strategy = SMACrossoverStrategy(fast_window=2, slow_window=4)

    # Construct candle sequence where fast crosses above slow then drops below
    # Prices: 10, 10, 10, 10 (flat), 20 (jump -> fast crosses slow), 5 (drop -> fast crosses below slow)
    prices = [10.0, 10.0, 10.0, 10.0, 20.0, 5.0]
    history = []

    signals = []
    for i, p in enumerate(prices):
        c = Candle(
            timestamp=f"2023-01-01T{i:02d}:00:00",
            open=p,
            high=p + 1,
            low=p - 1,
            close=p,
            volume=100.0,
        )
        history.append(c)
        signals.append(strategy.next(c, history))

    # Expect HOLD for first 4 candles (insufficient history or no cross)
    assert signals[0] == Signal.HOLD
    assert signals[1] == Signal.HOLD
    assert signals[2] == Signal.HOLD
    assert signals[3] == Signal.HOLD

    # Candle 5 (price 20): fast SMA = (10+20)/2 = 15, slow SMA = (10+10+10+20)/4 = 12.5 -> BUY signal
    assert signals[4] == Signal.BUY

    # Candle 6 (price 5): fast SMA = (20+5)/2 = 12.5, slow SMA = (10+10+20+5)/4 = 11.25
    # Prev fast = 15, prev slow = 12.5
    # Next step with price 2.0 to force fast < slow
    c_drop = Candle(
        timestamp="2023-01-01T06:00:00",
        open=2.0,
        high=2.0,
        low=1.0,
        close=2.0,
        volume=100.0,
    )
    history.append(c_drop)
    sig_drop = strategy.next(c_drop, history)
    assert sig_drop == Signal.SELL

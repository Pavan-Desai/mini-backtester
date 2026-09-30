"""Tests confirming no future candle lookahead in backtest engine."""

from typing import List, Sequence
import pytest

from minibacktester.engine import BacktestEngine
from minibacktester.models import Candle, Signal
from minibacktester.strategy import Strategy


class LookaheadCheckerStrategy(Strategy):
    """Strategy that verifies history contains only past and current candles."""

    def __init__(self, expected_total_candles: int):
        self.expected_total = expected_total_candles
        self.history_lengths: List[int] = []
        self.seen_timestamps: List[str] = []

    def next(self, candle: Candle, history: Sequence[Candle]) -> Signal:
        # Assert history length grows incrementally: 1, 2, 3...
        expected_len = len(self.history_lengths) + 1
        assert len(history) == expected_len, f"Expected history length {expected_len}, got {len(history)}"

        # Assert history length is never equal to total candles before the end
        assert len(history) <= self.expected_total

        # Assert last element in history matches current candle
        assert history[-1] == candle

        # Assert current candle timestamp matches expected sequence
        self.history_lengths.append(len(history))
        self.seen_timestamps.append(str(candle.timestamp))

        return Signal.HOLD


def test_no_lookahead_enforcement(sample_candles):
    """Verify strategy strictly receives sequential history without future candles."""
    total = len(sample_candles)
    strategy = LookaheadCheckerStrategy(expected_total_candles=total)
    engine = BacktestEngine(initial_capital=10000.0)

    result = engine.run(strategy, sample_candles)

    # Check history grew step by step from 1 to total
    assert strategy.history_lengths == list(range(1, total + 1))
    assert strategy.seen_timestamps == [str(c.timestamp) for c in sample_candles]
    assert len(result.equity_curve) == total

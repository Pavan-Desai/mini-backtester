"""Simple Moving Average Crossover Strategy."""

from typing import Sequence

from minibacktester.models import Candle, Signal
from minibacktester.strategy import Strategy


class SMACrossoverStrategy(Strategy):
    """Simple Moving Average (SMA) Crossover Strategy.

    Generates Signal.BUY when fast SMA crosses above slow SMA.
    Generates Signal.SELL when fast SMA crosses below slow SMA.
    Generates Signal.HOLD otherwise or if history is insufficient.
    """

    def __init__(self, fast_window: int = 5, slow_window: int = 20) -> None:
        """Initialize strategy with fast and slow windows.

        Args:
            fast_window: Period for fast SMA. Must be >= 1.
            slow_window: Period for slow SMA. Must be > fast_window.
        """
        if fast_window < 1:
            raise ValueError("fast_window must be at least 1")
        if slow_window <= fast_window:
            raise ValueError("slow_window must be greater than fast_window")

        self.fast_window = fast_window
        self.slow_window = slow_window

    def next(self, candle: Candle, history: Sequence[Candle]) -> Signal:
        """Evaluate crossover on historical candle closes.

        Args:
            candle: Current candle.
            history: Sequence of historical candles including current candle.

        Returns:
            Signal: BUY, SELL, or HOLD.
        """
        if len(history) < self.slow_window + 1:
            return Signal.HOLD

        # Extract close prices
        closes = [c.close for c in history]

        # Calculate current SMAs
        current_fast = sum(closes[-self.fast_window:]) / self.fast_window
        current_slow = sum(closes[-self.slow_window:]) / self.slow_window

        # Calculate previous SMAs (1 candle prior)
        prev_fast = sum(closes[-self.fast_window - 1 : -1]) / self.fast_window
        prev_slow = sum(closes[-self.slow_window - 1 : -1]) / self.slow_window

        # Check for crossover
        if prev_fast <= prev_slow and current_fast > current_slow:
            return Signal.BUY
        elif prev_fast >= prev_slow and current_fast < current_slow:
            return Signal.SELL

        return Signal.HOLD

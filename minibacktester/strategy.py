"""Strategy interface for mini-backtester."""

from abc import ABC, abstractmethod
from typing import Sequence

from minibacktester.models import Candle, Signal


class Strategy(ABC):
    """Abstract base class for all backtesting strategies.

    Strategies receive the current candle and full history up to the current candle
    to decide on trading signals.
    """

    @abstractmethod
    def next(self, candle: Candle, history: Sequence[Candle]) -> Signal:
        """Evaluate the current market state and generate a trading signal.

        Args:
            candle: The current candle being processed.
            history: Historical candles up to and including the current candle.
                     The last element of history is equal to `candle`.

        Returns:
            Signal: Signal.BUY, Signal.SELL, or Signal.HOLD.
        """
        pass

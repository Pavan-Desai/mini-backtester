"""Core data models and enumerations for mini-backtester."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union


class Signal(Enum):
    """Trading signal emitted by a strategy."""

    BUY = auto()
    SELL = auto()
    HOLD = auto()


class PositionSide(Enum):
    """Side of an open or closed position."""

    FLAT = auto()
    LONG = auto()
    SHORT = auto()


@dataclass(frozen=True)
class Candle:
    """OHLCV market candle representing price action over a single interval.

    Attributes:
        timestamp: Datetime or timestamp string representing candle time.
        open: Opening price.
        high: Highest price during interval.
        low: Lowest price during interval.
        close: Closing price.
        volume: Traded volume during interval.
    """

    timestamp: Union[datetime, str]
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

    def __post_init__(self) -> None:
        """Validate candle fields."""
        if self.open < 0 or self.high < 0 or self.low < 0 or self.close < 0:
            raise ValueError("Prices must be non-negative")
        if self.low > self.open or self.low > self.close or self.low > self.high:
            raise ValueError("Low price cannot be higher than open, close, or high")
        if self.high < self.open or self.high < self.close:
            raise ValueError("High price cannot be lower than open or close")
        if self.volume < 0:
            raise ValueError("Volume must be non-negative")

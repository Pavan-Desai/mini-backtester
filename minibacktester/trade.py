"""Completed trade record representation."""

from dataclasses import dataclass
from datetime import datetime
from typing import Union

from minibacktester.models import PositionSide


@dataclass(frozen=True)
class Trade:
    """Record of a completed trade.

    Attributes:
        entry_time: Timestamp when position was opened.
        exit_time: Timestamp when position was closed.
        side: Position side (LONG or SHORT).
        size: Quantity traded.
        entry_price: Average entry price.
        exit_price: Average exit price.
        pnl: Realized profit and loss in cash amount.
        return_pct: Realized percentage return on trade (e.g., 0.05 for +5%).
    """

    entry_time: Union[datetime, str]
    exit_time: Union[datetime, str]
    side: PositionSide
    size: float
    entry_price: float
    exit_price: float
    pnl: float
    return_pct: float

"""Position tracking and management."""

from datetime import datetime
from typing import Optional, Union

from minibacktester.models import PositionSide
from minibacktester.trade import Trade


class Position:
    """Represents an active trading position."""

    def __init__(
        self,
        side: PositionSide,
        size: float,
        entry_price: float,
        entry_time: Union[datetime, str],
    ) -> None:
        """Initialize a position.

        Args:
            side: PositionSide.LONG or PositionSide.SHORT.
            size: Quantity/units of asset.
            entry_price: Entry price per unit.
            entry_time: Timestamp of position entry.
        """
        if side not in (PositionSide.LONG, PositionSide.SHORT):
            raise ValueError("Position side must be LONG or SHORT")
        if size <= 0:
            raise ValueError("Position size must be positive")
        if entry_price <= 0:
            raise ValueError("Entry price must be positive")

        self.side = side
        self.size = size
        self.entry_price = entry_price
        self.entry_time = entry_time

    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized PnL at current market price.

        Args:
            current_price: Current market price.

        Returns:
            Unrealized profit/loss.
        """
        if self.side == PositionSide.LONG:
            return (current_price - self.entry_price) * self.size
        else:
            return (self.entry_price - current_price) * self.size

    def market_value(self, current_price: float) -> float:
        """Calculate market value of the position.

        Args:
            current_price: Current market price.

        Returns:
            Market value in cash terms.
        """
        if self.side == PositionSide.LONG:
            return self.size * current_price
        else:
            # For short position, entry value + unrealized PnL
            return (self.size * self.entry_price) + self.unrealized_pnl(current_price)

    def close(self, exit_price: float, exit_time: Union[datetime, str]) -> Trade:
        """Close position at exit_price and return completed Trade object.

        Args:
            exit_price: Price at which position is closed.
            exit_time: Timestamp of position exit.

        Returns:
            Completed Trade instance.
        """
        if exit_price <= 0:
            raise ValueError("Exit price must be positive")

        pnl = self.unrealized_pnl(exit_price)
        initial_value = self.size * self.entry_price
        return_pct = pnl / initial_value if initial_value > 0 else 0.0

        return Trade(
            entry_time=self.entry_time,
            exit_time=exit_time,
            side=self.side,
            size=self.size,
            entry_price=self.entry_price,
            exit_price=exit_price,
            pnl=round(pnl, 6),
            return_pct=round(return_pct, 6),
        )

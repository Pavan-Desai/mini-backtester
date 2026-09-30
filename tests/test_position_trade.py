"""Tests for Position and Trade management."""

import pytest

from minibacktester.models import PositionSide
from minibacktester.position import Position
from minibacktester.trade import Trade


def test_position_validation():
    """Test invalid input validation for Position."""
    with pytest.raises(ValueError, match="Position side must be LONG or SHORT"):
        Position(PositionSide.FLAT, 10.0, 100.0, "2023-01-01")

    with pytest.raises(ValueError, match="Position size must be positive"):
        Position(PositionSide.LONG, -5.0, 100.0, "2023-01-01")

    with pytest.raises(ValueError, match="Entry price must be positive"):
        Position(PositionSide.LONG, 10.0, -100.0, "2023-01-01")


def test_long_position_lifecycle():
    """Test unrealized PnL, market value, and close trade for Long position."""
    pos = Position(
        side=PositionSide.LONG,
        size=10.0,
        entry_price=100.0,
        entry_time="2023-01-01T00:00:00",
    )

    # Price stays same
    assert pos.unrealized_pnl(100.0) == 0.0
    assert pos.market_value(100.0) == 1000.0

    # Price goes up
    assert pos.unrealized_pnl(110.0) == 100.0
    assert pos.market_value(110.0) == 1100.0

    # Close position at 110
    trade = pos.close(exit_price=110.0, exit_time="2023-01-02T00:00:00")
    assert isinstance(trade, Trade)
    assert trade.side == PositionSide.LONG
    assert trade.size == 10.0
    assert trade.entry_price == 100.0
    assert trade.exit_price == 110.0
    assert trade.pnl == 100.0
    assert trade.return_pct == 0.10


def test_short_position_lifecycle():
    """Test unrealized PnL and close trade for Short position."""
    pos = Position(
        side=PositionSide.SHORT,
        size=5.0,
        entry_price=200.0,
        entry_time="2023-01-01T00:00:00",
    )

    # Price goes down -> profit on short
    assert pos.unrealized_pnl(180.0) == 100.0  # (200 - 180) * 5

    # Close position at 180
    trade = pos.close(exit_price=180.0, exit_time="2023-01-02T00:00:00")
    assert trade.side == PositionSide.SHORT
    assert trade.pnl == 100.0
    assert trade.return_pct == 0.10  # 100 / 1000

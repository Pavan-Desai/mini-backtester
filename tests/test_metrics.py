"""Tests for performance metrics calculations."""

import math
import pytest

from minibacktester.metrics import (
    calculate_max_drawdown,
    calculate_profit_factor,
    calculate_total_return,
    calculate_win_rate,
    compute_performance_metrics,
)
from minibacktester.models import PositionSide
from minibacktester.trade import Trade


def test_calculate_total_return():
    """Test total return calculation."""
    assert calculate_total_return(10000.0, 12000.0) == 0.20
    assert calculate_total_return(10000.0, 8000.0) == -0.20
    assert calculate_total_return(0.0, 100.0) == 0.0


def test_calculate_win_rate_and_profit_factor():
    """Test win rate and profit factor edge cases."""
    # No trades
    assert calculate_win_rate([]) == 0.0
    assert calculate_profit_factor([]) == 0.0

    t1 = Trade("t1", "t2", PositionSide.LONG, 1, 100, 120, pnl=20.0, return_pct=0.20)
    t2 = Trade("t1", "t2", PositionSide.LONG, 1, 100, 90, pnl=-10.0, return_pct=-0.10)
    trades = [t1, t2]

    assert calculate_win_rate(trades) == 0.50
    assert calculate_profit_factor(trades) == 2.0  # 20 / 10

    # Only winning trades -> Profit factor = Inf
    winning_only = [t1]
    assert calculate_profit_factor(winning_only) == float("inf")

    # Only losing trades -> Profit factor = 0
    losing_only = [t2]
    assert calculate_profit_factor(losing_only) == 0.0


def test_calculate_max_drawdown():
    """Test maximum drawdown calculation."""
    assert calculate_max_drawdown([]) == 0.0

    # Curve: 100 -> 150 -> 120 (20% dd from 150) -> 200 -> 100 (50% dd from 200) -> 180
    equity = [100.0, 150.0, 120.0, 200.0, 100.0, 180.0]
    assert pytest.approx(calculate_max_drawdown(equity), rel=1e-4) == 0.50


def test_compute_performance_metrics():
    """Test comprehensive metrics dataclass computation."""
    t1 = Trade("t1", "t2", PositionSide.LONG, 1, 100, 110, pnl=10.0, return_pct=0.10)
    equity = [1000.0, 1100.0]

    metrics = compute_performance_metrics(1000.0, equity, [t1])
    d = metrics.to_dict()

    assert d["initial_capital"] == 1000.0
    assert d["final_equity"] == 1100.0
    assert d["total_return"] == 0.10
    assert d["num_trades"] == 1.0
    assert d["winning_trades"] == 1.0
    assert d["win_rate"] == 1.0

"""Performance metrics calculation for backtest evaluation."""

from dataclasses import dataclass
from typing import Dict, List, Sequence

from minibacktester.trade import Trade


@dataclass(frozen=True)
class PerformanceMetrics:
    """Summary metrics for backtest performance.

    Attributes:
        initial_capital: Starting capital.
        final_equity: Final portfolio equity.
        total_return: Total return percentage (0.10 = 10%).
        num_trades: Total number of completed trades.
        winning_trades: Number of profitable trades (pnl > 0).
        losing_trades: Number of loss trades (pnl < 0).
        win_rate: Percentage of winning trades (0.0 to 1.0).
        profit_factor: Gross profit divided by gross loss.
        max_drawdown: Maximum peak-to-trough percentage drawdown.
    """

    initial_capital: float
    final_equity: float
    total_return: float
    num_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float

    def to_dict(self) -> Dict[str, float]:
        """Return metrics dictionary."""
        return {
            "initial_capital": round(self.initial_capital, 2),
            "final_equity": round(self.final_equity, 2),
            "total_return": round(self.total_return, 6),
            "num_trades": float(self.num_trades),
            "winning_trades": float(self.winning_trades),
            "losing_trades": float(self.losing_trades),
            "win_rate": round(self.win_rate, 6),
            "profit_factor": round(self.profit_factor, 6),
            "max_drawdown": round(self.max_drawdown, 6),
        }


def calculate_total_return(initial_capital: float, final_equity: float) -> float:
    """Calculate total return percentage."""
    if initial_capital <= 0:
        return 0.0
    return (final_equity - initial_capital) / initial_capital


def calculate_win_rate(trades: Sequence[Trade]) -> float:
    """Calculate win rate as fraction of winning trades over total trades."""
    if not trades:
        return 0.0
    winning = sum(1 for t in trades if t.pnl > 0)
    return winning / len(trades)


def calculate_profit_factor(trades: Sequence[Trade]) -> float:
    """Calculate profit factor (gross profit / gross loss).

    Returns inf if there are profits but no losses, and 0.0 if there are no profits.
    """
    if not trades:
        return 0.0

    gross_profit = sum(t.pnl for t in trades if t.pnl > 0)
    gross_loss = abs(sum(t.pnl for t in trades if t.pnl < 0))

    if gross_loss == 0.0:
        return float("inf") if gross_profit > 0 else 0.0

    return gross_profit / gross_loss


def calculate_max_drawdown(equity_curve: Sequence[float]) -> float:
    """Calculate maximum peak-to-trough percentage drawdown.

    Args:
        equity_curve: Sequence of equity values over time.

    Returns:
        Max drawdown as a positive fraction (e.g., 0.25 for 25% drawdown).
    """
    if not equity_curve:
        return 0.0

    peak = equity_curve[0]
    max_dd = 0.0

    for value in equity_curve:
        if value > peak:
            peak = value
        elif peak > 0:
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd

    return max_dd


def compute_performance_metrics(
    initial_capital: float,
    equity_curve: Sequence[float],
    trades: Sequence[Trade],
) -> PerformanceMetrics:
    """Compute all performance metrics for a backtest run."""
    final_equity = equity_curve[-1] if equity_curve else initial_capital
    tot_return = calculate_total_return(initial_capital, final_equity)
    num_trades = len(trades)
    winning_trades = sum(1 for t in trades if t.pnl > 0)
    losing_trades = sum(1 for t in trades if t.pnl < 0)
    win_rate = calculate_win_rate(trades)
    profit_factor = calculate_profit_factor(trades)
    max_dd = calculate_max_drawdown(equity_curve)

    return PerformanceMetrics(
        initial_capital=initial_capital,
        final_equity=final_equity,
        total_return=tot_return,
        num_trades=num_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        win_rate=win_rate,
        profit_factor=profit_factor,
        max_drawdown=max_dd,
    )

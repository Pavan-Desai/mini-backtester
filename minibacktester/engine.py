"""Backtest Engine for candle-by-candle simulation."""

from dataclasses import dataclass
from typing import List, Optional, Sequence

from minibacktester.models import Candle, PositionSide, Signal
from minibacktester.metrics import PerformanceMetrics, compute_performance_metrics
from minibacktester.position import Position
from minibacktester.strategy import Strategy
from minibacktester.trade import Trade


@dataclass
class BacktestResult:
    """Complete results from a backtest execution.

    Attributes:
        equity_curve: List of equity values at each candle close.
        trades: List of all completed trades.
        metrics: Computed performance metrics.
        timestamps: List of candle timestamps.
    """

    equity_curve: List[float]
    trades: List[Trade]
    metrics: PerformanceMetrics
    timestamps: List[str]


class BacktestEngine:
    """Sequential backtesting engine that runs a strategy on OHLCV candles."""

    def __init__(
        self,
        initial_capital: float = 10000.0,
        allow_short: bool = False,
        commission_pct: float = 0.0,
    ) -> None:
        """Initialize the backtest engine.

        Args:
            initial_capital: Starting cash balance.
            allow_short: Whether short positions are allowed on SELL signal when FLAT.
            commission_pct: Transaction fee percentage per trade (e.g. 0.001 for 0.1%).
        """
        if initial_capital <= 0:
            raise ValueError("Initial capital must be positive")
        if commission_pct < 0:
            raise ValueError("Commission percentage cannot be negative")

        self.initial_capital = initial_capital
        self.allow_short = allow_short
        self.commission_pct = commission_pct

    def run(self, strategy: Strategy, candles: Sequence[Candle]) -> BacktestResult:
        """Execute backtest sequentially over provided candles.

        Args:
            strategy: Strategy instance to generate signals.
            candles: Sequence of market candles ordered chronologically.

        Returns:
            BacktestResult object containing equity curve, completed trades, and metrics.
        """
        if not candles:
            empty_metrics = compute_performance_metrics(
                self.initial_capital, [self.initial_capital], []
            )
            return BacktestResult(
                equity_curve=[self.initial_capital],
                trades=[],
                metrics=empty_metrics,
                timestamps=[],
            )

        cash = self.initial_capital
        position: Optional[Position] = None
        trades: List[Trade] = []
        equity_curve: List[float] = []
        timestamps: List[str] = []
        history: List[Candle] = []

        for candle in candles:
            # Enforce sequential no-lookahead history up to current candle
            history.append(candle)
            timestamps.append(str(candle.timestamp))

            # Query strategy signal given strictly past & current data
            # Passing a tuple / copy prevents strategy from modifying internal history
            signal = strategy.next(candle, tuple(history))

            # Handle signal execution at current candle close
            current_price = candle.close

            if signal == Signal.BUY:
                if position is None:
                    # Open LONG position using available cash
                    buy_amount = cash * (1.0 - self.commission_pct)
                    size = buy_amount / current_price
                    if size > 0:
                        position = Position(
                            side=PositionSide.LONG,
                            size=size,
                            entry_price=current_price,
                            entry_time=candle.timestamp,
                        )
                        cash = 0.0

                elif position.side == PositionSide.SHORT:
                    # Close SHORT position and open LONG position
                    trade = position.close(current_price, candle.timestamp)
                    trades.append(trade)
                    # Realize cash from closing short
                    cash += (position.size * position.entry_price) + trade.pnl
                    cash *= (1.0 - self.commission_pct)

                    # Open LONG with available cash
                    size = (cash * (1.0 - self.commission_pct)) / current_price
                    if size > 0:
                        position = Position(
                            side=PositionSide.LONG,
                            size=size,
                            entry_price=current_price,
                            entry_time=candle.timestamp,
                        )
                        cash = 0.0
                    else:
                        position = None

            elif signal == Signal.SELL:
                if position is not None and position.side == PositionSide.LONG:
                    # Close LONG position
                    trade = position.close(current_price, candle.timestamp)
                    trades.append(trade)
                    cash = (position.size * current_price) * (1.0 - self.commission_pct)
                    position = None

                    if self.allow_short:
                        # Open SHORT position with available cash
                        short_amount = cash * (1.0 - self.commission_pct)
                        size = short_amount / current_price
                        if size > 0:
                            position = Position(
                                side=PositionSide.SHORT,
                                size=size,
                                entry_price=current_price,
                                entry_time=candle.timestamp,
                            )

                elif position is None and self.allow_short:
                    # Open SHORT position
                    short_amount = cash * (1.0 - self.commission_pct)
                    size = short_amount / current_price
                    if size > 0:
                        position = Position(
                            side=PositionSide.SHORT,
                            size=size,
                            entry_price=current_price,
                            entry_time=candle.timestamp,
                        )

            # Calculate current total equity
            if position is None:
                current_equity = cash
            elif position.side == PositionSide.LONG:
                current_equity = position.size * current_price
            else:  # SHORT position
                unrealized_pnl = (position.entry_price - current_price) * position.size
                current_equity = cash + unrealized_pnl

            equity_curve.append(round(current_equity, 4))

        # Auto-close open position at final candle to finalize backtest trades
        if position is not None and len(candles) > 0:
            final_candle = candles[-1]
            trade = position.close(final_candle.close, final_candle.timestamp)
            trades.append(trade)
            if position.side == PositionSide.LONG:
                cash = (position.size * final_candle.close) * (1.0 - self.commission_pct)
            else:
                cash = cash + trade.pnl
            position = None
            equity_curve[-1] = round(cash, 4)

        metrics = compute_performance_metrics(self.initial_capital, equity_curve, trades)

        return BacktestResult(
            equity_curve=equity_curve,
            trades=trades,
            metrics=metrics,
            timestamps=timestamps,
        )

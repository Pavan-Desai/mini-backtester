"""Package exports for minibacktester."""

from minibacktester.data import generate_crossover_candles, generate_synthetic_candles
from minibacktester.engine import BacktestEngine, BacktestResult
from minibacktester.models import Candle, PositionSide, Signal
from minibacktester.position import Position
from minibacktester.strategy import Strategy
from minibacktester.strategies.sma_crossover import SMACrossoverStrategy
from minibacktester.trade import Trade

__all__ = [
    "Candle",
    "Signal",
    "PositionSide",
    "Strategy",
    "Position",
    "Trade",
    "BacktestEngine",
    "BacktestResult",
    "SMACrossoverStrategy",
    "generate_synthetic_candles",
    "generate_crossover_candles",
]

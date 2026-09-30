"""Synthetic dataset generator for testing backtesting strategies."""

from datetime import datetime, timedelta
from typing import List

from minibacktester.models import Candle


def generate_synthetic_candles(
    num_candles: int = 100,
    start_price: float = 100.0,
    start_time: str = "2023-01-01T00:00:00",
    interval_minutes: int = 60,
    trend: float = 0.001,
    volatility: float = 0.01,
    seed: int = 42,
) -> List[Candle]:
    """Generate synthetic OHLCV candle data deterministically.

    Args:
        num_candles: Number of candles to generate.
        start_price: Initial price.
        start_time: ISO format string for start timestamp.
        interval_minutes: Time step between candles in minutes.
        trend: Multiplicative drift factor per step.
        volatility: Volatility factor per step.
        seed: Random seed for reproducibility.

    Returns:
        List of Candle objects.
    """
    import random

    rng = random.Random(seed)
    current_time = datetime.fromisoformat(start_time)
    current_price = start_price
    candles: List[Candle] = []

    for _ in range(num_candles):
        change_pct = trend + (rng.uniform(-1.0, 1.0) * volatility)
        open_price = current_price
        close_price = max(0.01, open_price * (1.0 + change_pct))

        # Generate realistic high/low around open and close
        high_price = max(open_price, close_price) * (1.0 + rng.uniform(0.001, volatility))
        low_price = min(open_price, close_price) * (1.0 - rng.uniform(0.001, volatility))
        low_price = max(0.01, low_price)
        volume = max(100.0, rng.uniform(500.0, 5000.0))

        candles.append(
            Candle(
                timestamp=current_time.isoformat(),
                open=round(open_price, 4),
                high=round(high_price, 4),
                low=round(low_price, 4),
                close=round(close_price, 4),
                volume=round(volume, 2),
            )
        )

        current_price = close_price
        current_time += timedelta(minutes=interval_minutes)

    return candles


def generate_crossover_candles() -> List[Candle]:
    """Generate deterministic candles designed to trigger SMA crossovers.

    Candles start low, rise steadily to trigger a golden cross (BUY),
    then fall sharply to trigger a death cross (SELL).

    Returns:
        List of Candle objects.
    """
    prices = (
        [100.0] * 10
        + [100.0 + i * 2.0 for i in range(1, 15)]  # Uptrend
        + [130.0 - i * 2.5 for i in range(1, 15)]  # Downtrend
        + [95.0] * 10
    )

    candles: List[Candle] = []
    base_time = datetime.fromisoformat("2023-01-01T00:00:00")

    for i, p in enumerate(prices):
        candles.append(
            Candle(
                timestamp=(base_time + timedelta(hours=i)).isoformat(),
                open=round(p, 2),
                high=round(p + 1.0, 2),
                low=round(p - 1.0, 2),
                close=round(p, 2),
                volume=1000.0,
            )
        )

    return candles

"""Pytest fixtures for backtester unit tests."""

from typing import List
import pytest

from minibacktester.data import generate_crossover_candles, generate_synthetic_candles
from minibacktester.models import Candle


@pytest.fixture
def sample_candles() -> List[Candle]:
    """Fixture returning 50 synthetic candles."""
    return generate_synthetic_candles(num_candles=50, seed=123)


@pytest.fixture
def crossover_candles() -> List[Candle]:
    """Fixture returning crossover candles."""
    return generate_crossover_candles()


@pytest.fixture
def simple_flat_candles() -> List[Candle]:
    """Fixture returning flat price candles."""
    return [
        Candle(
            timestamp=f"2023-01-01T{i:02d}:00:00",
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.0,
            volume=1000.0,
        )
        for i in range(15)
    ]

# Mini-Backtester

A lightweight, clean, and extensible Python backtesting engine built for quantitative trading strategies.

## Overview

`mini-backtester` provides a modular event-driven (candle-by-candle) backtesting framework without external market data dependencies or heavy frameworks. It enforces strict sequential historical data access to guarantee no-lookahead bias during strategy backtesting.

## Architecture

The project is structured cleanly into distinct logical modules:

```
minibacktester/
├── __init__.py           # Package API exports
├── models.py             # Data classes (Candle, Signal, PositionSide)
├── strategy.py           # Abstract Strategy base class
├── position.py           # Position tracking and mark-to-market valuation
├── trade.py              # Completed Trade record representation
├── engine.py            # Candle-by-candle BacktestEngine
├── metrics.py           # Performance metrics calculations (return, win rate, drawdown, etc.)
├── data.py               # Deterministic synthetic OHLCV data generators
├── cli.py                # Command-line interface
└── strategies/
    └── sma_crossover.py  # Simple Moving Average Crossover Strategy
```

### Key Architectural Concepts
- **`Candle`**: Immutable representation of OHLCV market candles with built-in validation.
- **`Strategy`**: Abstract interface defining `next(candle, history)`. History passed to strategies is strictly limited to past and current candles.
- **`Position`**: Tracks open position state (LONG or SHORT), position size, entry price, and calculates unrealized profit and loss.
- **`Trade`**: Immutable record of closed trades capturing entry/exit prices, timestamps, realized profit/loss, and return percentage.
- **`BacktestEngine`**: Processes OHLCV candles sequentially, evaluates strategy signals, manages portfolio cash/equity, and records trades.
- **`PerformanceMetrics`**: Computes standard performance statistics including Total Return, Win Rate, Profit Factor, and Maximum Drawdown.

---

## Installation

No external dependencies are required beyond Python 3.8+ and standard library modules. `pytest` is used for running tests.

```bash
# Clone the repository
git clone https://github.com/your-repo/mini-backtester.git
cd mini-backtester
```

---

## Usage

### 1. Command-Line Interface (CLI)

Run backtests directly using the built-in CLI:

```bash
# Run with default crossover dataset
python3 -m minibacktester.cli --fast-window 3 --slow-window 10 --dataset crossover

# Run with synthetic dataset and custom capital
python3 -m minibacktester.cli --initial-capital 50000 --fast-window 5 --slow-window 20 --dataset synthetic --candles 200
```

### 2. Python API

```python
from minibacktester import BacktestEngine, SMACrossoverStrategy, generate_crossover_candles

# 1. Load or generate candles
candles = generate_crossover_candles()

# 2. Instantiate strategy and engine
strategy = SMACrossoverStrategy(fast_window=3, slow_window=10)
engine = BacktestEngine(initial_capital=10000.0, commission_pct=0.001)

# 3. Run backtest
result = engine.run(strategy, candles)

# 4. Access performance metrics and trades
metrics = result.metrics
print(f"Final Equity: ${metrics.final_equity:,.2f}")
print(f"Total Return: {metrics.total_return * 100:+.2f}%")
print(f"Win Rate:     {metrics.win_rate * 100:.1f}%")
print(f"Max Drawdown: {metrics.max_drawdown * 100:.2f}%")

for trade in result.trades:
    print(f"Trade {trade.side.name}: PnL=${trade.pnl:+.2f} ({trade.return_pct * 100:+.2f}%)")
```

---

## Example Output

Running `python3 -m minibacktester.cli --fast-window 3 --slow-window 10 --dataset crossover`:

```text
============================================================
           MINI-BACKTESTER RUNNER
============================================================
Initial Capital : $10,000.00
Strategy        : SMA Crossover (Fast: 3, Slow: 10)
Dataset         : crossover
Candles Count   : 48
------------------------------------------------------------

============================================================
           BACKTEST RESULTS METRICS
============================================================
Final Equity     : $11,764.71
Total Return     : +17.65%
Total Trades     : 1
Winning Trades   : 1
Losing Trades    : 0
Win Rate         : 100.0%
Profit Factor    : Inf
Max Drawdown     : 6.25%
------------------------------------------------------------

COMPLETED TRADES:
  Trade 01: Side=LONG  | Entry= 102.00 @ 2023-01-01T10:00:00 | Exit= 120.00 @ 2023-01-02T03:00:00 | PnL=$+1764.71 (+17.65%)
============================================================
```

---

## Testing

Run the full pytest suite:

```bash
PYTHONPATH=. pytest -v
```

The test suite covers:
- Strategy signal generation and window validations
- Sequential candle processing in backtest engine
- Strict no-lookahead enforcement (ensuring future candles are never leaked)
- Position entry, exit, and unrealized/realized PnL calculation
- Metrics calculation (Total Return, Win Rate, Profit Factor, Max Drawdown) and division-by-zero edge cases
- CLI interface and parameter parsing

---

## Design Decisions

1. **Strict No-Lookahead History Isolation**: The engine converts history to an immutable tuple `tuple(history)` on each step, ensuring strategies cannot look ahead to future candles or modify historical state.
2. **Zero External Dependencies**: Implemented entirely in standard Python without Pandas/Numpy overhead to ensure lightweight and fast execution.
3. **Immutable Trade & Candle Records**: `Candle` and `Trade` dataclasses are frozen to guarantee data integrity throughout backtest execution.
4. **Robust Edge Case Handling**: Metrics functions explicitly handle zero-trade, zero-loss (infinite profit factor), and zero-initial-capital scenarios.

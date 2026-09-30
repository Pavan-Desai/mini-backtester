"""Command-line interface for running backtests."""

import argparse
import sys
from typing import List, Optional

from minibacktester.data import generate_crossover_candles, generate_synthetic_candles
from minibacktester.engine import BacktestEngine
from minibacktester.strategies.sma_crossover import SMACrossoverStrategy


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run SMA Crossover backtest on synthetic OHLCV data."
    )
    parser.add_argument(
        "--initial-capital",
        type=float,
        default=10000.0,
        help="Initial capital balance (default: 10000.0)",
    )
    parser.add_argument(
        "--fast-window",
        type=int,
        default=5,
        help="Fast SMA window size (default: 5)",
    )
    parser.add_argument(
        "--slow-window",
        type=int,
        default=20,
        help="Slow SMA window size (default: 20)",
    )
    parser.add_argument(
        "--candles",
        type=int,
        default=100,
        help="Number of synthetic candles to generate (default: 100)",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        choices=["synthetic", "crossover"],
        default="crossover",
        help="Dataset type to run ('synthetic' or 'crossover', default: 'crossover')",
    )
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> None:
    """Main CLI execution routine."""
    parsed = parse_args(args)

    print("=" * 60)
    print("           MINI-BACKTESTER RUNNER")
    print("=" * 60)
    print(f"Initial Capital : ${parsed.initial_capital:,.2f}")
    print(f"Strategy        : SMA Crossover (Fast: {parsed.fast_window}, Slow: {parsed.slow_window})")
    print(f"Dataset         : {parsed.dataset}")

    if parsed.dataset == "crossover":
        candles = generate_crossover_candles()
    else:
        candles = generate_synthetic_candles(num_candles=parsed.candles)

    print(f"Candles Count   : {len(candles)}")
    print("-" * 60)

    strategy = SMACrossoverStrategy(
        fast_window=parsed.fast_window,
        slow_window=parsed.slow_window,
    )
    engine = BacktestEngine(initial_capital=parsed.initial_capital)
    result = engine.run(strategy, candles)

    m = result.metrics
    print("\n" + "=" * 60)
    print("           BACKTEST RESULTS METRICS")
    print("=" * 60)
    print(f"Final Equity     : ${m.final_equity:,.2f}")
    print(f"Total Return     : {m.total_return * 100:+.2f}%")
    print(f"Total Trades     : {m.num_trades}")
    print(f"Winning Trades   : {m.winning_trades}")
    print(f"Losing Trades    : {m.losing_trades}")
    print(f"Win Rate         : {m.win_rate * 100:.1f}%")
    pf_str = f"{m.profit_factor:.2f}" if m.profit_factor != float("inf") else "Inf"
    print(f"Profit Factor    : {pf_str}")
    print(f"Max Drawdown     : {m.max_drawdown * 100:.2f}%")
    print("-" * 60)

    if result.trades:
        print("\nCOMPLETED TRADES:")
        for idx, trade in enumerate(result.trades, 1):
            print(
                f"  Trade {idx:02d}: Side={trade.side.name:<5} | Entry={trade.entry_price:>7.2f} @ {trade.entry_time} "
                f"| Exit={trade.exit_price:>7.2f} @ {trade.exit_time} | PnL=${trade.pnl:>+8.2f} ({trade.return_pct * 100:>+6.2f}%)"
            )
    else:
        print("\nNo trades executed during the backtest.")

    print("=" * 60)


if __name__ == "__main__":
    main()

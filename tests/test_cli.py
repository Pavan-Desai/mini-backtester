"""Tests for CLI entrypoint execution."""

from minibacktester.cli import main, parse_args


def test_cli_parse_args():
    """Test parsing CLI arguments."""
    args = parse_args(["--initial-capital", "5000", "--fast-window", "3", "--slow-window", "10", "--dataset", "synthetic"])
    assert args.initial_capital == 5000.0
    assert args.fast_window == 3
    assert args.slow_window == 10
    assert args.dataset == "synthetic"


def test_cli_main_execution(capsys):
    """Test executing CLI main function and stdout output."""
    main(["--fast-window", "3", "--slow-window", "10", "--dataset", "crossover"])
    captured = capsys.readouterr()

    assert "MINI-BACKTESTER RUNNER" in captured.out
    assert "Initial Capital : $10,000.00" in captured.out
    assert "BACKTEST RESULTS METRICS" in captured.out
    assert "Total Return" in captured.out

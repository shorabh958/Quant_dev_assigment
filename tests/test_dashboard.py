from pathlib import Path

import pandas as pd


def test_demo_trade_file_exists():
    path = Path("data/demo_trades.csv")

    assert path.exists()

    data = pd.read_csv(path)

    assert not data.empty
    assert "side" in data.columns
    assert "price" in data.columns


def test_trade_report_has_valid_prices():
    data = pd.read_csv("data/demo_trades.csv")

    assert (data["price"] > 0).all()
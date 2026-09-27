import pandas as pd

from trading.data_provider import (
    YahooDataProvider,
)


def test_provider_class_exists():

    provider = YahooDataProvider(
        "^NSEI"
    )

    assert provider.symbol == "^NSEI"


def test_provider_schema(monkeypatch):

    class FakeTicker:

        def history(
            self,
            period,
            interval,
            auto_adjust,
        ):

            return pd.DataFrame(
                {
                    "Open": [100.0],
                    "High": [101.0],
                    "Low": [99.0],
                    "Close": [100.5],
                    "Volume": [1000],
                }
            )

    monkeypatch.setattr(
        "trading.data_provider.yf.Ticker",
        lambda symbol: FakeTicker(),
    )

    data = YahooDataProvider().fetch()

    assert list(data.columns) == [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    assert len(data) == 1
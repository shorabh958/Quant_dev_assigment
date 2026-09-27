from __future__ import annotations

from dataclasses import dataclass
import pandas as pd
import yfinance as yf


@dataclass
class YahooDataProvider:
    symbol: str = "^NSEI"

    def fetch(self, period="2y", interval="1d"):
        data = yf.Ticker(self.symbol).history(
            period=period,
            interval=interval,
            auto_adjust=False,
        )

        if data.empty:
            raise ValueError(
                f"No market data returned for {self.symbol}"
            )

        data = data.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
        )

        return data[
            [
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]
        ].dropna()
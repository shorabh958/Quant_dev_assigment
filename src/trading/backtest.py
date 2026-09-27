from dataclasses import dataclass
from decimal import Decimal

import pandas as pd

from .models import Candle, Fill, Side
from .portfolio import Portfolio
from .strategies import GridStrategy


@dataclass
class BacktestConfig:
    slippage_bps: float = 1.0
    fee_per_order: Decimal = Decimal("20")


class BacktestEngine:
    def __init__(
        self,
        strategy: GridStrategy,
        config: BacktestConfig | None = None,
    ):
        self.strategy = strategy
        self.config = config or BacktestConfig()

    def run(self, data: pd.DataFrame) -> Portfolio:
        portfolio = Portfolio()

        reference_price = float(data.iloc[0]["close"])

        for timestamp, row in data.iterrows():
            candle = Candle(
                timestamp=timestamp,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
            )

            # ATR must already be present and is based only on prior data.
            atr_value = float(row["atr"])

            signal = self.strategy.generate_signal(
                candle=candle,
                atr_value=atr_value,
                reference_price=reference_price,
            )

            if signal is None:
                continue

            # Conservative bar-accurate assumption:
            # signal generated from close -> fill at next available price
            # is preferable to pretending we knew the future.
            fill_price = Decimal(str(candle.close))

            slippage = Decimal(str(self.config.slippage_bps / 10000))

            if signal.side == Side.BUY:
                fill_price *= 1 + slippage
            else:
                fill_price *= 1 - slippage

            fill = Fill(
                order_id=f"BT-{timestamp}",
                timestamp=timestamp,
                side=signal.side,
                quantity=1,
                price=fill_price,
                fees=self.config.fee_per_order,
            )

            portfolio.apply_fill(fill)

        return portfolio
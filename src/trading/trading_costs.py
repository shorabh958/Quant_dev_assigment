from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CostModel:
    brokerage_per_order: Decimal = Decimal("20")
    slippage_bps: Decimal = Decimal("1")
    exchange_fee_bps: Decimal = Decimal("0.5")
    tax_bps: Decimal = Decimal("0.0")

    def slippage(
        self,
        price: Decimal,
        side: str,
    ) -> Decimal:

        price = Decimal(str(price))

        rate = (
            self.slippage_bps
            / Decimal("10000")
        )

        return price * rate

    def execution_price(
        self,
        price: Decimal,
        side: str,
    ) -> Decimal:

        price = Decimal(str(price))

        impact = self.slippage(
            price,
            side,
        )

        if side == "BUY":
            return price + impact

        return price - impact

    def variable_cost(
        self,
        price: Decimal,
        quantity: int,
    ) -> Decimal:

        price = Decimal(str(price))

        notional = (
            price
            * Decimal(quantity)
        )

        rate = (
            self.exchange_fee_bps
            + self.tax_bps
        ) / Decimal("10000")

        return notional * rate

    def total_cost(
        self,
        price: Decimal,
        quantity: int,
    ) -> Decimal:

        return (
            self.brokerage_per_order
            + self.variable_cost(
                price,
                quantity,
            )
        )

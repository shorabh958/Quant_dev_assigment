from __future__ import annotations

from decimal import Decimal

from .contracts import ContractRegistry


class MarketRuleEngine:

    def __init__(self, registry):
        self.registry = registry

    def validate_order(
        self,
        symbol: str,
        quantity: int,
        price: float,
    ):

        contract = self.registry.get(symbol)

        if not self.registry.validate_quantity(
            symbol,
            quantity,
        ):
            raise ValueError(
                f"Quantity {quantity} is not "
                f"a valid multiple of lot size "
                f"{contract.lot_size}"
            )

        tick = Decimal(
            str(contract.tick_size)
        )

        price_decimal = Decimal(
            str(price)
        )

        ticks = price_decimal / tick

        if ticks != ticks.to_integral_value():
            raise ValueError(
                f"Price {price} does not "
                f"match tick size "
                f"{contract.tick_size}"
            )

        return True

    def round_price(
        self,
        symbol: str,
        price: float,
    ):

        contract = self.registry.get(symbol)

        tick = Decimal(
            str(contract.tick_size)
        )

        value = Decimal(
            str(price)
        )

        rounded = (
            value / tick
        ).quantize(
            Decimal("1")
        ) * tick

        return float(rounded)
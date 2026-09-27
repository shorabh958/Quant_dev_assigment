from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Contract:
    # Keep the original positional API:
    # Contract(symbol, exchange, lot_size, tick_size, expiry)
    symbol: str
    exchange: str
    lot_size: int
    tick_size: float
    expiry: date

    # New metadata is optional and therefore does not break
    # existing callers.
    segment: str = "NFO"
    instrument_type: str = "FUT"


class ContractRegistry:

    def __init__(self):
        self._contracts: dict[str, Contract] = {}

    def add(self, contract: Contract):

        if contract.lot_size <= 0:
            raise ValueError(
                "lot_size must be positive"
            )

        if contract.tick_size <= 0:
            raise ValueError(
                "tick_size must be positive"
            )

        self._contracts[
            contract.symbol
        ] = contract

    def get(self, symbol: str) -> Contract:
        return self._contracts[symbol]

    def contains(self, symbol: str) -> bool:
        return symbol in self._contracts

    def validate_quantity(
        self,
        symbol: str,
        quantity: int,
    ) -> bool:

        contract = self.get(symbol)

        return (
            quantity > 0
            and quantity % contract.lot_size == 0
        )

    def normalize_quantity(
        self,
        symbol: str,
        quantity: int,
    ) -> int:

        contract = self.get(symbol)

        if quantity <= 0:
            return 0

        return (
            quantity // contract.lot_size
        ) * contract.lot_size

    def remove_expired(
        self,
        today: date,
    ):

        self._contracts = {
            symbol: contract
            for symbol, contract
            in self._contracts.items()
            if contract.expiry >= today
        }

    def symbols(self):
        return list(self._contracts)
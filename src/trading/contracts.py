from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Contract:
    symbol: str
    exchange: str
    lot_size: int
    tick_size: float
    expiry: date


class ContractRegistry:
    def __init__(self):
        self._contracts: dict[str, Contract] = {}

    def add(self, contract: Contract):
        self._contracts[contract.symbol] = contract

    def get(self, symbol: str) -> Contract:
        return self._contracts[symbol]

    def remove_expired(self, today: date):
        self._contracts = {
            k: v for k, v in self._contracts.items()
            if v.expiry >= today
        }

    def symbols(self):
        return list(self._contracts)
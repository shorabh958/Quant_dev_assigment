from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ExpiryContract:
    symbol: str
    exchange: str
    expiry: date
    lot_size: int
    tick_size: float


class RolloverManager:

    def __init__(self, contracts):
        self.contracts = sorted(
            contracts,
            key=lambda x: x.expiry,
        )

    def active_contract(self, today: date):
        valid = [
            c for c in self.contracts
            if c.expiry >= today
        ]

        if not valid:
            raise ValueError(
                "No valid contract available"
            )

        return valid[0]

    def next_contract(
        self,
        current: ExpiryContract,
    ):
        for contract in self.contracts:
            if contract.expiry > current.expiry:
                return contract

        raise ValueError(
            "No rollover contract available"
        )

    def should_roll(
        self,
        contract: ExpiryContract,
        today: date,
        days_before_expiry: int = 3,
    ):
        days = (
            contract.expiry - today
        ).days

        return 0 <= days <= days_before_expiry
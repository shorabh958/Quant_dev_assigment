from datetime import date

from trading.rollover import (
    ExpiryContract,
    RolloverManager,
)


def contracts():
    return [
        ExpiryContract(
            "NIFTY-FUT-1",
            "NSE",
            date(2026, 10, 29),
            65,
            0.05,
        ),
        ExpiryContract(
            "NIFTY-FUT-2",
            "NSE",
            date(2026, 11, 26),
            65,
            0.05,
        ),
    ]


def test_active_contract():

    manager = RolloverManager(
        contracts()
    )

    active = manager.active_contract(
        date(2026, 10, 1)
    )

    assert active.symbol == "NIFTY-FUT-1"


def test_rollover_detection():

    manager = RolloverManager(
        contracts()
    )

    contract = contracts()[0]

    assert manager.should_roll(
        contract,
        date(2026, 10, 27),
        days_before_expiry=3,
    )


def test_next_contract():

    manager = RolloverManager(
        contracts()
    )

    next_contract = manager.next_contract(
        contracts()[0]
    )

    assert (
        next_contract.symbol
        == "NIFTY-FUT-2"
    )
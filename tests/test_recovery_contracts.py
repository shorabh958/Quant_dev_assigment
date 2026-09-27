from datetime import date

import pytest

from trading.contracts import (
    Contract,
    ContractRegistry,
)

from trading.recovery import (
    StateStore,
    RecoveryManager,
    reconcile_position,
)

from trading.execution import (
    ManagedOrder,
    OrderState,
)

from trading.market_rules import (
    MarketRuleEngine,
)


def make_registry():

    registry = ContractRegistry()

    registry.add(
        Contract(
            symbol="NIFTY26SEP",
            exchange="NSE",
            segment="NFO",
            lot_size=65,
            tick_size=0.05,
            expiry=date(
                2026,
                9,
                30,
            ),
        )
    )

    return registry


def test_contract_lot_size():

    registry = make_registry()

    assert registry.validate_quantity(
        "NIFTY26SEP",
        65,
    )

    assert registry.validate_quantity(
        "NIFTY26SEP",
        130,
    )

    assert not registry.validate_quantity(
        "NIFTY26SEP",
        70,
    )


def test_quantity_normalization():

    registry = make_registry()

    assert (
        registry.normalize_quantity(
            "NIFTY26SEP",
            130,
        )
        == 130
    )

    assert (
        registry.normalize_quantity(
            "NIFTY26SEP",
            100,
        )
        == 65
    )


def test_market_tick_size():

    registry = make_registry()

    rules = MarketRuleEngine(
        registry
    )

    assert rules.validate_order(
        "NIFTY26SEP",
        65,
        25000.05,
    )


def test_invalid_tick_price():

    registry = make_registry()

    rules = MarketRuleEngine(
        registry
    )

    with pytest.raises(ValueError):

        rules.validate_order(
            "NIFTY26SEP",
            65,
            25000.03,
        )


def test_state_persists_and_recovers(tmp_path):

    path = (
        tmp_path
        / "state.json"
    )

    store = StateStore(path)

    order = ManagedOrder(
        client_id="ORDER-1",
        symbol="NIFTY",
        side="BUY",
        quantity=65,
        filled_quantity=65,
        state=OrderState.FILLED,
    )

    store.save(
        {
            order.client_id: order
        }
    )

    recovered = store.load()

    assert "ORDER-1" in recovered

    assert (
        recovered["ORDER-1"].state
        == OrderState.FILLED
    )

    assert (
        recovered["ORDER-1"].filled_quantity
        == 65
    )


def test_recovery_manager():

    store = StateStore(
        "data/test_state.json"
    )

    manager = RecoveryManager(
        store
    )

    order = ManagedOrder(
        client_id="RECOVERY-1",
        symbol="NIFTY",
        side="SELL",
        quantity=65,
        filled_quantity=65,
        state=OrderState.FILLED,
    )

    manager.checkpoint(
        {
            order.client_id: order
        }
    )

    recovered = manager.recover()

    assert (
        recovered["RECOVERY-1"].state
        == OrderState.FILLED
    )


def test_position_reconciliation_match():

    result = reconcile_position(
        "NIFTY",
        65,
        65,
    )

    assert result.matched
    assert result.difference == 0


def test_position_reconciliation_mismatch():

    result = reconcile_position(
        "NIFTY",
        65,
        130,
    )

    assert not result.matched
    assert result.difference == 65
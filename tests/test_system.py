from datetime import date
import pytest

from trading.alerts import AlertManager
from trading.config import EngineConfig
from trading.contracts import Contract, ContractRegistry
from trading.execution import (
    ManagedOrder,
    OrderState,
    OrderStateMachine,
)
from trading.macro import MacroAdapter
from trading.metrics import (
    max_drawdown,
    sharpe_ratio,
    total_return,
)
from trading.recovery import StateStore
from trading.walkforward import generate_windows


def test_contract_registry():
    registry = ContractRegistry()

    registry.add(
        Contract(
            "NIFTY",
            "NSE",
            75,
            0.05,
            date(2026, 12, 31),
        )
    )

    assert registry.get("NIFTY").lot_size == 75


def test_order_state_machine():
    machine = OrderStateMachine()

    order = ManagedOrder(
        "O1",
        "NIFTY",
        "BUY",
        2,
    )

    machine.submit(order)
    machine.update("O1", 2, OrderState.FILLED)

    assert machine.orders["O1"].state == OrderState.FILLED
    assert machine.orders["O1"].filled_quantity == 2


def test_order_idempotency():
    machine = OrderStateMachine()

    order = ManagedOrder("O1", "NIFTY", "BUY", 1)

    first = machine.submit(order)
    second = machine.submit(order)

    assert first is second
    assert len(machine.orders) == 1


def test_state_recovery(tmp_path):
    path = tmp_path / "state.json"

    orders = {
        "O1": ManagedOrder(
            "O1",
            "NIFTY",
            "BUY",
            1,
            1,
            OrderState.FILLED,
        )
    }

    store = StateStore(str(path))
    store.save(orders)

    restored = store.load()

    assert restored["O1"].state == OrderState.FILLED


def test_metrics():
    equity = [100, 110, 105, 120]

    assert total_return(equity) == pytest.approx(0.20)
    assert max_drawdown(equity) > 0
    assert sharpe_ratio([0.01, 0.02, -0.01]) != 0


def test_walk_forward():
    import pandas as pd

    data = pd.DataFrame({"close": range(20)})

    windows = list(
        generate_windows(
            data,
            train_size=10,
            test_size=5,
        )
    )

    assert len(windows) == 2
    assert len(windows[0].train) == 10
    assert len(windows[0].test) == 5


def test_macro_adapter():
    adapter = MacroAdapter()

    adapter.add("equity", 2, 1)
    adapter.add("volatility", -1, 1)

    assert adapter.score() == 0.5


def test_config():
    config = EngineConfig()

    assert config.max_position == 3
    assert config.trading_enabled


def test_alert_manager():
    assert AlertManager() is not None
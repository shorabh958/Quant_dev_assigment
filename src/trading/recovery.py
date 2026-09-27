import json
from dataclasses import asdict
from pathlib import Path

from .execution import ManagedOrder, OrderState


class StateStore:
    def __init__(self, path: str = "data/state.json"):
        self.path = Path(path)

    def save(self, orders: dict[str, ManagedOrder]):
        self.path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            key: {
                **asdict(order),
                "state": order.state.value,
            }
            for key, order in orders.items()
        }

        self.path.write_text(json.dumps(payload, indent=2))

    def load(self) -> dict[str, ManagedOrder]:
        if not self.path.exists():
            return {}

        raw = json.loads(self.path.read_text())

        return {
            key: ManagedOrder(
                client_id=value["client_id"],
                symbol=value["symbol"],
                side=value["side"],
                quantity=value["quantity"],
                filled_quantity=value["filled_quantity"],
                state=OrderState(value["state"]),
            )
            for key, value in raw.items()
        }
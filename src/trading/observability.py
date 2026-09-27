from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class TradeRecord:
    timestamp: datetime
    symbol: str
    side: str
    quantity: int
    price: float
    order_id: str
    strategy: str
    pnl: float = 0.0


class JsonLogger:
    def __init__(self, name: str = "quant_engine"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)

    def event(self, event: str, **fields):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **fields,
        }
        self.logger.info(json.dumps(payload, default=str))


class TradeBlotter:
    def __init__(self):
        self.trades: list[TradeRecord] = []

    def record(self, trade: TradeRecord):
        self.trades.append(trade)

    def export_csv(self, path: str | Path):
        path = Path(path)

        if not self.trades:
            path.write_text("")
            return

        import csv

        rows = [asdict(t) for t in self.trades]

        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    @property
    def total_pnl(self) -> float:
        return sum(t.pnl for t in self.trades)
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReconciliationReport:
    orders_checked: int
    positions_checked: int
    order_mismatches: int
    position_mismatches: int

    @property
    def clean(self):
        return (
            self.order_mismatches == 0
            and self.position_mismatches == 0
        )


class ReconciliationEngine:

    def compare_positions(
        self,
        local_positions,
        broker_positions,
    ):

        symbols = (
            set(local_positions)
            | set(broker_positions)
        )

        mismatches = 0

        for symbol in symbols:

            local = local_positions.get(
                symbol,
                0,
            )

            broker = broker_positions.get(
                symbol,
                0,
            )

            if local != broker:
                mismatches += 1

        return mismatches

    def compare_orders(
        self,
        local_orders,
        broker_orders,
    ):

        mismatches = 0

        for order_id in (
            set(local_orders)
            | set(broker_orders)
        ):

            local = local_orders.get(
                order_id
            )

            broker = broker_orders.get(
                order_id
            )

            if local != broker:
                mismatches += 1

        return mismatches

    def reconcile(
        self,
        local_orders,
        broker_orders,
        local_positions,
        broker_positions,
    ):

        order_mismatches = (
            self.compare_orders(
                local_orders,
                broker_orders,
            )
        )

        position_mismatches = (
            self.compare_positions(
                local_positions,
                broker_positions,
            )
        )

        return ReconciliationReport(
            orders_checked=len(
                set(local_orders)
                | set(broker_orders)
            ),
            positions_checked=len(
                set(local_positions)
                | set(broker_positions)
            ),
            order_mismatches=order_mismatches,
            position_mismatches=position_mismatches,
        )
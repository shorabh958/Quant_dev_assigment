from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ReconciliationSummary:
    rows_compared: int
    pnl_difference: float
    quantity_difference: float
    price_difference: float
    matched: bool


class SpreadsheetReconciler:

    def compare(
        self,
        engine: pd.DataFrame,
        desk: pd.DataFrame,
        pnl_tolerance: float = 0.01,
        quantity_tolerance: int = 0,
        price_tolerance: float = 0.01,
    ) -> ReconciliationSummary:

        required = {
            "quantity",
            "price",
            "pnl",
        }

        for frame_name, frame in (
            ("engine", engine),
            ("desk", desk),
        ):
            missing = required - set(frame.columns)

            if missing:
                raise ValueError(
                    f"{frame_name} missing columns: "
                    f"{sorted(missing)}"
                )

        rows = min(
            len(engine),
            len(desk),
        )

        if rows == 0:
            return ReconciliationSummary(
                0,
                0.0,
                0.0,
                0.0,
                True,
            )

        engine = engine.iloc[:rows].reset_index(
            drop=True
        )
        desk = desk.iloc[:rows].reset_index(
            drop=True
        )

        pnl_difference = abs(
            float(engine["pnl"].sum())
            - float(desk["pnl"].sum())
        )

        quantity_difference = abs(
            float(engine["quantity"].sum())
            - float(desk["quantity"].sum())
        )

        price_difference = abs(
            float(engine["price"].mean())
            - float(desk["price"].mean())
        )

        matched = (
            pnl_difference <= pnl_tolerance
            and quantity_difference <= quantity_tolerance
            and price_difference <= price_tolerance
        )

        return ReconciliationSummary(
            rows_compared=rows,
            pnl_difference=pnl_difference,
            quantity_difference=quantity_difference,
            price_difference=price_difference,
            matched=matched,
        )
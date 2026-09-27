import pandas as pd

from trading.reconciliation_report import (
    SpreadsheetReconciler,
)


def test_matching_spreadsheets():

    data = pd.DataFrame(
        {
            "quantity": [1, -1],
            "price": [100, 101],
            "pnl": [0, 1],
        }
    )

    result = SpreadsheetReconciler().compare(
        data,
        data.copy(),
    )

    assert result.matched
    assert result.rows_compared == 2


def test_detects_pnl_difference():

    engine = pd.DataFrame(
        {
            "quantity": [1],
            "price": [100],
            "pnl": [10],
        }
    )

    desk = pd.DataFrame(
        {
            "quantity": [1],
            "price": [100],
            "pnl": [12],
        }
    )

    result = SpreadsheetReconciler().compare(
        engine,
        desk,
        pnl_tolerance=0.01,
    )

    assert not result.matched
    assert result.pnl_difference == 2


def test_detects_price_difference():

    engine = pd.DataFrame(
        {
            "quantity": [1],
            "price": [100],
            "pnl": [10],
        }
    )

    desk = pd.DataFrame(
        {
            "quantity": [1],
            "price": [105],
            "pnl": [10],
        }
    )

    result = SpreadsheetReconciler().compare(
        engine,
        desk,
    )

    assert not result.matched
    assert result.price_difference == 5
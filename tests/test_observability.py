from datetime import datetime, timezone

from trading.observability import JsonLogger, TradeBlotter, TradeRecord


def test_trade_blotter_records_trade():
    blotter = TradeBlotter()

    blotter.record(
        TradeRecord(
            timestamp=datetime.now(timezone.utc),
            symbol="NIFTY",
            side="BUY",
            quantity=1,
            price=25000,
            order_id="O1",
            strategy="grid",
            pnl=100,
        )
    )

    assert len(blotter.trades) == 1
    assert blotter.total_pnl == 100


def test_blotter_exports_csv(tmp_path):
    blotter = TradeBlotter()

    blotter.record(
        TradeRecord(
            timestamp=datetime.now(timezone.utc),
            symbol="NIFTY",
            side="SELL",
            quantity=1,
            price=25000,
            order_id="O2",
            strategy="reverse",
        )
    )

    path = tmp_path / "trades.csv"
    blotter.export_csv(path)

    assert path.exists()
    assert "NIFTY" in path.read_text()


def test_logger_exists():
    logger = JsonLogger()
    assert logger.logger.name == "quant_engine"
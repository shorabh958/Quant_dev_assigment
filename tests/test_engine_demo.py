from pathlib import Path
import subprocess
import sys


def test_demo_engine_runs():

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_demo.py",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    assert "QUANT DEVELOPMENT ENGINE" in result.stdout

    assert "ATR Grid Strategy" in result.stdout

    assert "Macro Regime Engine" in result.stdout

    assert Path("data/demo_trades.csv").exists()
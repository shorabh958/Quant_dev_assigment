from trading.risk import RiskManager, RiskConfig
from trading.strategies import StopAndReverseStrategy


def test_position_cap():
    risk = RiskManager(RiskConfig(max_position=3))

    assert risk.allowed_quantity(2, 1) == 1
    assert risk.allowed_quantity(3, 1) == 0


def test_pyramiding_limit():
    risk = RiskManager(RiskConfig(max_pyramids=3))

    assert risk.can_pyramid(2)
    assert not risk.can_pyramid(3)


def test_kill_switch():
    risk = RiskManager(RiskConfig(max_daily_loss=5000))

    assert not risk.kill_switch(-4999)
    assert risk.kill_switch(-5000)
    assert risk.kill_switch(-6000)


def test_stop_and_reverse():
    strategy = StopAndReverseStrategy(threshold=10)

    # Existing short -> price breaks upward -> reverse long.
    signal = strategy.generate_signal(
        price=112,
        reference_price=100,
        current_position=-1,
    )

    assert signal is not None
    assert signal.side.value == "BUY"

    # Existing long -> price breaks downward -> reverse short.
    signal = strategy.generate_signal(
        price=88,
        reference_price=100,
        current_position=1,
    )

    assert signal is not None
    assert signal.side.value == "SELL"
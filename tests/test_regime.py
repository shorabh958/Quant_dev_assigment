from trading.regime import (
    CircuitBreaker,
    MacroRegimeEngine,
    MacroSnapshot,
    Regime,
)


def test_risk_on_regime():
    engine = MacroRegimeEngine()

    snapshot = MacroSnapshot(
        equity_return=4,
        volatility=1,
        interest_rate_change=-1,
        dollar_change=-1,
    )

    assert engine.classify(snapshot) == Regime.RISK_ON


def test_crisis_regime():
    engine = MacroRegimeEngine()

    snapshot = MacroSnapshot(
        equity_return=-5,
        volatility=12,
        interest_rate_change=2,
        dollar_change=2,
    )

    assert engine.classify(snapshot) == Regime.CRISIS


def test_crisis_disables_trading():
    engine = MacroRegimeEngine()

    params = engine.parameters(Regime.CRISIS)

    assert params.trading_enabled is False
    assert params.position_multiplier == 0


def test_risk_off_reduces_position():
    engine = MacroRegimeEngine()

    params = engine.parameters(Regime.RISK_OFF)

    assert params.trading_enabled
    assert params.position_multiplier < 1


def test_circuit_breaker():
    breaker = CircuitBreaker()

    assert not breaker.triggered(0.05, -1000, 3)
    assert breaker.triggered(0.11, -1000, 3)
    assert breaker.triggered(0.05, -6000, 3)
    assert breaker.triggered(0.05, -1000, 11)
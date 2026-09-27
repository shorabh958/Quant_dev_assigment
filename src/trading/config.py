from dataclasses import dataclass


@dataclass(frozen=True)
class EngineConfig:
    max_position: int = 3
    max_daily_loss: float = 5000
    slippage_bps: float = 1
    reconnect_attempts: int = 5
    heartbeat_seconds: int = 10
    trading_enabled: bool = True
from dataclasses import dataclass


@dataclass
class RiskConfig:
    max_position: int = 3
    max_pyramids: int = 3
    max_daily_loss: float = 5000.0


class RiskManager:
    def __init__(self, config: RiskConfig | None = None):
        self.config = config or RiskConfig()

    def allowed_quantity(self, current_position: int, requested: int) -> int:
        remaining = self.config.max_position - abs(current_position)
        return max(0, min(requested, remaining))

    def kill_switch(self, daily_pnl: float) -> bool:
        return daily_pnl <= -self.config.max_daily_loss
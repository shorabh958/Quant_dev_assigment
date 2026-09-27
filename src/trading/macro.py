from dataclasses import dataclass


@dataclass(frozen=True)
class MacroProxy:
    name: str
    value: float
    weight: float


class MacroAdapter:
    """Normalizes external macro inputs before the regime engine."""

    def __init__(self, proxies: list[MacroProxy] | None = None):
        self.proxies = proxies or []

    def add(self, name: str, value: float, weight: float = 1.0):
        self.proxies.append(
            MacroProxy(name, value, weight)
        )

    def score(self) -> float:
        if not self.proxies:
            return 0.0

        total_weight = sum(abs(p.weight) for p in self.proxies)

        if total_weight == 0:
            return 0.0

        return sum(
            p.value * p.weight
            for p in self.proxies
        ) / total_weight
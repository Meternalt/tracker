from dataclasses import dataclass
from datetime import date


@dataclass
class SpecialPeriod:
    name: str
    start: date
    end: date
    hp_penalty_multiplier: float = 0.0
    xp_multiplier: float = 0.5

    def is_active(self, today: date | None = None) -> bool:
        today = today or date.today()
        return self.start <= today <= self.end

    def days_left(self) -> int:
        return max(0, (self.end - date.today()).days)
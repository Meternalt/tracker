from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class Habit:
    name: str
    xp_reward: int
    hp_penalty: int
    gold_reward: int = 0
    streak: int = 0
    last_done: date | None = None
    linked_goal: str | None = None

    def __post_init__(self):
        if self.gold_reward == 0:
            self.gold_reward = self.xp_reward // 2

    def complete(self) -> dict:
        today = date.today()
        if self.last_done == today:
            return {"error": "Уже выполнено сегодня"}

        if self.last_done == today - timedelta(days=1):
            self.streak += 1
        else:
            self.streak = 1

        self.last_done = today
        streak_bonus = self.streak * 2

        return {
            "xp": self.xp_reward + streak_bonus,
            "gold": self.gold_reward + self.streak,
            "streak": self.streak,
        }

    def is_done_today(self) -> bool:
        return self.last_done == date.today()

    def is_missed(self) -> bool:
        if self.last_done is None:
            return False
        return self.last_done < date.today() - timedelta(days=1)
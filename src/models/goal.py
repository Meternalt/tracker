from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class GoalStatus(Enum):
    ACTIVE = "active"
    DONE = "done"
    EXPIRED = "expired"


class Difficulty(Enum):
    SMALL = ("Маленькая", 100)
    MEDIUM = ("Средняя", 300)
    BIG = ("Большая", 700)
    EPIC = ("Эпическая", 1500)

    def __init__(self, label, xp):
        self.label = label
        self.xp = xp


@dataclass
class Milestone:
    name: str
    xp_reward: int
    done: bool = False
    done_at: date | None = None

    def complete(self) -> int:
        if self.done:
            return 0
        self.done = True
        self.done_at = date.today()
        return self.xp_reward


@dataclass
class Goal:
    name: str
    difficulty: Difficulty
    deadline: date
    description: str = ""
    milestones: list[Milestone] = field(default_factory=list)
    status: GoalStatus = GoalStatus.ACTIVE
    created_at: date = field(default_factory=date.today)

    @property
    def total_xp(self) -> int:
        return self.difficulty.xp

    @property
    def progress(self) -> float:
        if not self.milestones:
            return 0.0
        done = sum(1 for m in self.milestones if m.done)
        return done / len(self.milestones)

    @property
    def days_left(self) -> int:
        return (self.deadline - date.today()).days

    def complete_milestone(self, name: str) -> dict:
        milestone = next(
            (m for m in self.milestones if m.name == name and not m.done),
            None,
        )
        if not milestone:
            return {"error": "Веха не найдена или уже выполнена"}

        xp = milestone.complete()
        result = {"xp": xp, "milestone": milestone.name}

        if all(m.done for m in self.milestones):
            self.status = GoalStatus.DONE
            result["goal_done"] = True
            result["bonus_xp"] = self.total_xp

        return result

    def is_overdue(self) -> bool:
        return self.status == GoalStatus.ACTIVE and date.today() > self.deadline
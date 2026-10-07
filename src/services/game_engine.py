import json
from datetime import date
from pathlib import Path
from src.models.character import Character
from src.models.habit import Habit
from src.models.goal import Goal, Milestone, Difficulty, GoalStatus
from src.models.special_period import SpecialPeriod
from src.services.shop import Shop
from src.services.goal_manager import GoalManager


class GameEngine:
    def __init__(self, save_path: str = "data/save.json"):
        self.save_path = Path(save_path)
        self.character = Character()
        self.habits: list[Habit] = []
        self.shop = Shop(self.character)
        self.goals = GoalManager()
        self._load()

    # Привычки
    DIFFICULTY_PRESETS = {
        "1": (10, 5, "Легко"),
        "2": (15, 10, "Средне"),
        "3": (25, 20, "Сложно"),
        "4": (50, 40, "Эпично"),
    }

    def add_habit(self, name: str, difficulty_key: str) -> Habit:
        xp, hp, _ = self.DIFFICULTY_PRESETS.get(
            difficulty_key, self.DIFFICULTY_PRESETS["2"])
        habit = Habit(name=name, xp_reward=xp, hp_penalty=hp)
        self.habits.append(habit)
        return habit

    def complete_habit(self, name: str) -> str:
        habit = next((h for h in self.habits if h.name == name), None)
        if not habit:
            return "Привычка не найдена"

        result = habit.complete()
        if "error" in result:
            return result["error"]

        xp = int(result["xp"] * self.character.xp_multiplier())
        if self.character.double_xp_charges > 0:
            xp *= 2
            self.character.double_xp_charges -= 1
            print("Двойной XP!")

        leveled = self.character.add_xp(xp)
        self.character.gold += result["gold"]

        msg = f"+{xp} XP, +{result['gold']} gold (streak: {result['streak']})"

        if habit.streak > 0 and habit.streak % 7 == 0:
            self.character.freeze_charges += 1
            msg += f"\nСерия {habit.streak}! +1 заморозка"

        return msg

    def use_freeze(self, name: str) -> str:
        habit = next((h for h in self.habits if h.name == name), None)
        if not habit:
            return "Привычка не найдена"
        if self.character.freeze_charges <= 0:
            return "Нет заморозок"

        self.character.freeze_charges -= 1
        habit.last_done = date.today()
        return f"Заморожено: {habit.name} (streak сохранён)"

    # Особые периоды
    def activate_period(self, name: str, days: int,
                        hp_mult: float = 0.0, xp_mult: float = 0.5) -> str:
        from datetime import timedelta
        period = SpecialPeriod(
            name=name,
            start=date.today(),
            end=date.today() + timedelta(days=days),
            hp_penalty_multiplier=hp_mult,
            xp_multiplier=xp_mult,
        )
        self.character.active_period = period
        return f"Активирован период «{name}» на {days} дн."

    def deactivate_period(self) -> str:
        self.character.active_period = None
        return "Период отменён."

    # Ежедневная проверка
    def daily_check(self):
        if self.character.is_protected():
            print("Щадящий режим - штрафов нет.")
        else:
            for habit in self.habits:
                if habit.is_missed():
                    dmg = int(habit.hp_penalty * self.character.hp_penalty_multiplier())
                    if dmg > 0:
                        self.character.take_damage(dmg)
                        print(f"Пропущено: {habit.name} (-{dmg} HP)")

        self.character.daily_recovery()

        for goal in self.goals.goals:
            if goal.is_overdue():
                goal.status = GoalStatus.EXPIRED

    # Сохранение
    def save(self):
        data = {
            "character": {
                **self.character.__dict__,
                "active_period": (
                    {
                        "name": self.character.active_period.name,
                        "start": str(self.character.active_period.start),
                        "end": str(self.character.active_period.end),
                        "hp_penalty_multiplier": self.character.active_period.hp_penalty_multiplier,
                        "xp_multiplier": self.character.active_period.xp_multiplier,
                    }
                    if self.character.active_period else None
                ),
                "sick_leave_until": (
                    str(self.character.sick_leave_until)
                    if self.character.sick_leave_until else None
                ),
            },
            "habits": [
                {
                    **h.__dict__,
                    "last_done": str(h.last_done) if h.last_done else None,
                }
                for h in self.habits
            ],
            "goals": [
                {
                    "name": g.name,
                    "difficulty": g.difficulty.name,
                    "deadline": str(g.deadline),
                    "description": g.description,
                    "status": g.status.name,
                    "milestones": [
                        {
                            "name": m.name,
                            "xp_reward": m.xp_reward,
                            "done": m.done,
                            "done_at": str(m.done_at) if m.done_at else None,
                        }
                        for m in g.milestones
                    ],
                }
                for g in self.goals.goals
            ],
        }
        self.save_path.parent.mkdir(exist_ok=True)
        self.save_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _load(self):
        if not self.save_path.exists():
            return
        try:
            data = json.loads(self.save_path.read_text(encoding="utf-8"))
        except Exception:
            return

        c_data = data.get("character", {})
        period_data = c_data.pop("active_period", None)
        sick_until = c_data.pop("sick_leave_until", None)

        self.character = Character(**c_data)
        if period_data:
            self.character.active_period = SpecialPeriod(
                name=period_data["name"],
                start=date.fromisoformat(period_data["start"]),
                end=date.fromisoformat(period_data["end"]),
                hp_penalty_multiplier=period_data["hp_penalty_multiplier"],
                xp_multiplier=period_data["xp_multiplier"],
            )
        if sick_until:
            self.character.sick_leave_until = date.fromisoformat(sick_until)

        self.shop = Shop(self.character)

        for h_data in data.get("habits", []):
            if h_data.get("last_done"):
                h_data["last_done"] = date.fromisoformat(h_data["last_done"])
            self.habits.append(Habit(**h_data))

        for g_data in data.get("goals", []):
            milestones = [
                Milestone(
                    name=m["name"],
                    xp_reward=m["xp_reward"],
                    done=m["done"],
                    done_at=date.fromisoformat(m["done_at"]) if m["done_at"] else None,
                )
                for m in g_data["milestones"]
            ]
            goal = Goal(
                name=g_data["name"],
                difficulty=Difficulty[g_data["difficulty"]],
                deadline=date.fromisoformat(g_data["deadline"]),
                description=g_data.get("description", ""),
                milestones=milestones,
                status=GoalStatus[g_data["status"]],
            )
            self.goals.goals.append(goal)
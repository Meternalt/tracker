import json
from datetime import date, timedelta
from pathlib import Path
from src.models.goal import Goal, Milestone, Difficulty, GoalStatus


class GoalManager:
    def __init__(self, templates_path: str = "data/goal_templates.json"):
        self.goals: list[Goal] = []
        self.templates = self._load_templates(templates_path)

    def _load_templates(self, path: str) -> dict:
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def create_from_template(self, name: str, category: str,
                             difficulty: Difficulty, days: int) -> Goal:
        template = self.templates.get(category, {})
        milestones = [
            Milestone(m["name"], m["xp"])
            for m in template.get("milestones", [])
        ]
        goal = Goal(
            name=name,
            difficulty=difficulty,
            deadline=date.today() + timedelta(days=days),
            milestones=milestones,
        )
        self.goals.append(goal)
        return goal

    def get_goal(self, name: str) -> Goal | None:
        return next((g for g in self.goals if g.name == name), None)

    def show_goals(self):
        print("\n=== ЦЕЛИ ===")
        if not self.goals:
            print("Пока нет целей.")
            return
        for i, g in enumerate(self.goals, 1):
            bar_len = 20
            filled = int(g.progress * bar_len)
            bar = "#" * filled + "." * (bar_len - filled)
            status = "[готово]" if g.status == GoalStatus.DONE else "[активна]"
            print(f"\n{i}. {g.name} {status}")
            print(f"   {g.difficulty.label} | до {g.deadline} "
                  f"(осталось {g.days_left} дн.)")
            print(f"   [{bar}] {int(g.progress * 100)}%")
            for m in g.milestones:
                mark = "[x]" if m.done else "[ ]"
                print(f"   {mark} {m.name} ({m.xp_reward} XP)")
from datetime import date
from src.services.game_engine import GameEngine
from src.models.goal import Difficulty


class ConsoleUI:
    def __init__(self, engine: GameEngine):
        self.engine = engine

    def run(self):
        self.engine.daily_check()

        while True:
            self.print_header()
            self.print_menu()

            choice = input("> ").strip().lower()

            if choice == "0":
                self.engine.save()
                print("Сохранено. До завтра!")
                break
            elif choice == "h":
                self.do_habit()
            elif choice == "n":
                self.new_habit()
            elif choice == "f":
                self.freeze_menu()
            elif choice == "s":
                self.shop_menu()
            elif choice == "g":
                self.goals_menu()
            elif choice == "p":
                self.period_menu()
            else:
                print("Неизвестная команда")

    def print_header(self):
        print("\n" + "=" * 50)
        print(self.engine.character)
        print("=" * 50)

    def print_menu(self):
        print("Привычки:")
        if not self.engine.habits:
            print("  (нет привычек)")
        for i, h in enumerate(self.engine.habits, 1):
            mark = "[x]" if h.is_done_today() else "[ ]"
            print(f"  {i}. {mark} {h.name} (streak: {h.streak}, "
                  f"XP {h.xp_reward})")
        print()
        print("[H] Выполнить  [N] Новая  [F] Заморозить  "
              "[S] Магазин  [G] Цели  [P] Период  [0] Выход")

    def do_habit(self):
        if not self.engine.habits:
            print("Сначала создай привычку.")
            return
        name = input("Название привычки: ").strip()
        print(self.engine.complete_habit(name))

    def new_habit(self):
        name = input("Название: ").strip()
        print("Сложность: 1 Легко, 2 Средне, 3 Сложно, 4 Эпично")
        diff = input("> ").strip()
        self.engine.add_habit(name, diff)
        print(f"Привычка «{name}» добавлена!")

    def freeze_menu(self):
        if not self.engine.habits:
            return
        print(f"Заморозок: {self.engine.character.freeze_charges}")
        name = input("Какую привычку заморозить? ").strip()
        print(self.engine.use_freeze(name))

    def shop_menu(self):
        self.engine.shop.show()
        print("\n[Enter] - назад, или введи ID товара для покупки")
        item_id = input("> ").strip()
        if item_id:
            print(self.engine.shop.buy(item_id))

    def goals_menu(self):
        self.engine.goals.show_goals()
        print("\n[N] Новая цель  [C] Отметить веху  [B] Назад")
        cmd = input("> ").strip().lower()
        if cmd == "n":
            self.create_goal_flow()
        elif cmd == "c":
            self.complete_milestone_flow()

    def create_goal_flow(self):
        name = input("Название цели: ").strip()
        print("Категория: learning, book, fitness, project, custom")
        cat = input("> ").strip() or "custom"
        print("Сложность: 1 Малая, 2 Средняя, 3 Большая, 4 Эпическая")
        diff_key = input("> ").strip()
        diff_map = {
            "1": Difficulty.SMALL,
            "2": Difficulty.MEDIUM,
            "3": Difficulty.BIG,
            "4": Difficulty.EPIC,
        }
        difficulty = diff_map.get(diff_key, Difficulty.MEDIUM)
        days = int(input("Дней до дедлайна: ").strip() or "30")

        goal = self.engine.goals.create_from_template(name, cat, difficulty, days)

        print(f"\nЦель «{goal.name}» создана с вехами:")
        for m in goal.milestones:
            print(f"   [ ] {m.name} ({m.xp_reward} XP)")

    def complete_milestone_flow(self):
        goal_name = input("Название цели: ").strip()
        goal = self.engine.goals.get_goal(goal_name)
        if not goal:
            print("Цель не найдена")
            return

        print("Вехи:")
        for i, m in enumerate(goal.milestones, 1):
            mark = "[x]" if m.done else "[ ]"
            print(f"  {i}. {mark} {m.name}")

        idx = int(input("Номер выполненной вехи: ").strip()) - 1
        if idx < 0 or idx >= len(goal.milestones):
            print("Неверно")
            return

        result = goal.complete_milestone(goal.milestones[idx].name)
        if "error" in result:
            print(result["error"])
            return

        xp = result["xp"]
        leveled = self.engine.character.add_xp(xp)
        print(f"+{xp} XP за веху!")

        if result.get("goal_done"):
            bonus = result["bonus_xp"]
            self.engine.character.add_xp(bonus)
            self.engine.character.gold += 200
            print(f"ЦЕЛЬ ДОСТИГНУТА! +{bonus} XP, +200 gold")

    def period_menu(self):
        c = self.engine.character
        if c.active_period and c.active_period.is_active():
            print(f"Активен: {c.active_period.name} "
                  f"(осталось {c.active_period.days_left()} дн.)")
            print("[C] Отменить  [Enter] Назад")
            if input("> ").strip().lower() == "c":
                print(self.engine.deactivate_period())
            return

        print("Особые периоды:")
        print("1. Месячные (5 дней)")
        print("2. Болезнь (3 дня)")
        print("3. Командировка (укажешь дни)")
        print("4. Взять выходной (осталось "
              f"{c.rest_days_left})")
        print("[Enter] Назад")
        ch = input("> ").strip()

        if ch == "1":
            print(self.engine.activate_period("Месячные", 5, 0.0, 0.5))
        elif ch == "2":
            print(self.engine.activate_period("Болезнь", 3, 0.0, 0.3))
        elif ch == "3":
            days = int(input("Сколько дней? ").strip() or "3")
            print(self.engine.activate_period("Командировка", days, 0.0, 0.5))
        elif ch == "4":
            if c.rest_days_left > 0:
                c.rest_days_left -= 1
                print(self.engine.activate_period("Выходной", 1, 0.0, 1.0))
            else:
                print("Выходные на неделе закончились")
from src.services.game_engine import GameEngine
from src.ui.console_ui import ConsoleUI


def main():
    engine = GameEngine()

    if not engine.habits:
        engine.add_habit("Зарядка", "2")
        engine.add_habit("Чтение 20 стр", "1")
        engine.add_habit("Без соцсетей до обеда", "3")

    ui = ConsoleUI(engine)
    ui.run()


if __name__ == "__main__":
    main()
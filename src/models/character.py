from dataclasses import dataclass, field
from datetime import date, timedelta
from src.models.special_period import SpecialPeriod


@dataclass
class Character:
    name: str = "Hero"
    level: int = 1
    xp: int = 0
    xp_max: int = 100
    hp: int = 100
    hp_max: int = 100
    gold: int = 0

    # Ресурсы
    freeze_charges: int = 3
    shield_charges: int = 0
    double_xp_charges: int = 0
    rest_days_left: int = 2

    # Состояния
    unlocked_skills: list[str] = field(default_factory=list)
    inventory: list[str] = field(default_factory=list)
    active_period: SpecialPeriod | None = None
    is_on_sick_leave: bool = False
    sick_leave_until: date | None = None

    # HP
    def take_damage(self, amount: int):
        if self.shield_charges > 0:
            self.shield_charges -= 1
            print("Амулет поглотил урон!")
            return
        self.hp = max(0, self.hp - amount)
        if self.hp == 0 and not self.is_on_sick_leave:
            self.enter_sick_leave()

    def heal(self, amount: int):
        self.hp = min(self.hp_max, self.hp + amount)

    def enter_sick_leave(self):
        self.is_on_sick_leave = True
        self.sick_leave_until = date.today() + timedelta(days=3)
        print("Ты заболел! 3 дня отдыха.")

    def daily_recovery(self):
        if self.is_on_sick_leave:
            self.heal(5)
            if self.hp >= self.hp_max * 0.5:
                self.is_on_sick_leave = False
                self.sick_leave_until = None
                print("Ты выздоровел!")

    # XP
    def add_xp(self, amount: int) -> bool:
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_max:
            self.xp -= self.xp_max
            self._level_up()
            leveled = True
        return leveled

    def _level_up(self):
        self.level += 1
        self.xp_max = int(self.xp_max * 1.5)
        self.hp_max += 10
        self.hp = self.hp_max
        print(f"LEVEL UP! Уровень {self.level}")

    # Защита
    def is_protected(self) -> bool:
        if self.is_on_sick_leave:
            return True
        if self.active_period and self.active_period.is_active():
            return True
        return False

    def hp_penalty_multiplier(self) -> float:
        if self.is_on_sick_leave:
            return 0.0
        if self.active_period and self.active_period.is_active():
            return self.active_period.hp_penalty_multiplier
        return 1.0

    def xp_multiplier(self) -> float:
        if self.active_period and self.active_period.is_active():
            return self.active_period.xp_multiplier
        return 1.0

    def __str__(self):
        status = ""
        if self.is_on_sick_leave:
            status = " [болен]"
        elif self.active_period and self.active_period.is_active():
            status = f" [{self.active_period.name}]"
        return (f"{self.name} Lvl {self.level}{status} | "
                f"XP {self.xp}/{self.xp_max} | HP {self.hp}/{self.hp_max} | "
                f"Gold {self.gold} | Freeze {self.freeze_charges}")
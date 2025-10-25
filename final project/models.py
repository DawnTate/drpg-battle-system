import math
from dataclasses import dataclass, field
import random
from skills import ALL_SKILLS, Skill 


@dataclass
class Player:
    row: int
    col: int
    hp: int = 15
    hp_max: int = 15
    sp_max: int = 10
    sp: int = 10
    skills: list = field(default_factory = lambda: ALL_SKILLS[:])
    atk_min: int = 3
    atk_max: int = 5
    level: int = 1
    exp: int = 0
    potions: int = 5
    sp_potions: int = 5

    crit_chance: float = 0.15       # 15% base crit chance
    crit_multiplier: float = 1.5    # crit deals 1.5x damage

    def is_alive(self) -> bool:
        return self.hp > 0

    def gain_exp(self, amount: int):
        """Gain EXP and handle level-up if threshold reached."""
        self.exp += amount
        while self.exp >= self.exp_to_next():
            self.exp -= self.exp_to_next()
            self.level_up()

    def exp_to_next(self) -> int:
        """EXP required to reach next level."""
        return 10 * self.level

    def level_up(self):
        """Increase player stats when leveling up."""
        self.level += 1
        self.hp_max += 5
        self.sp_max += 8
        self.atk_min += 3
        self.atk_max += 4
        self.crit_chance = min(self.crit_chance + 0.03, 1)
        self.hp = self.hp_max
        self.sp = self.sp_max
        print()
        print(f"*** Level Up! You are now Level {self.level}! ***")
        print(f"""Stats:        HP: {self.hp_max - 5} → {self.hp_max}, 
              SP={self.sp_max - 8} → {self.sp_max}
              ATK={self.atk_min - 3}-{self.atk_max - 4} → {self.atk_min}-{self.atk_max}, 
              Crit={self.crit_chance - 0.03} → {self.crit_chance}
              You have recoverd your HP and SP!
              """)
    
    # ---  roll player's damage with crit ---
    def roll_damage(self) -> tuple[int, bool]:
        """Return (damage, is_crit)."""
        base = random.randint(self.atk_min, self.atk_max)
        is_crit = (random.random() < self.crit_chance)
        dmg = int(base * self.crit_multiplier) if is_crit else base
        return dmg, is_crit
    
    def heal_percent(self, pct: float) -> None:
        """
        Restore a percentage of max HP and SP (e.g., pct=0.3 -> 30%).
        Values are clamped to max HP/SP.
        """
        hp_gain = max(1, math.ceil(self.hp_max * pct))
        sp_gain = max(1, math.ceil(self.sp_max * pct))
        self.hp = min(self.hp + hp_gain, self.hp_max)
        self.sp = min(self.sp + sp_gain, self.sp_max)

    def apply_permanent_boosts(self, delta: dict) -> None:
        """
        Permanently modify stats based on the 'delta' dictionary.
        Supported keys: 'hp_max', 'sp_max', 'atk_min', 'atk_max', 'crit_chance'.
        Values are additive; negative values represent backlash.
        """
        if 'hp_max' in delta:
            self.hp_max = max(1, self.hp_max + delta['hp_max'])
            self.hp = min(self.hp, self.hp_max)
        if 'sp_max' in delta:
            self.sp_max = max(1, self.sp_max + delta['sp_max'])
            self.sp = min(self.sp, self.sp_max)
        if 'atk_min' in delta:
            self.atk_min = max(1, self.atk_min + delta['atk_min'])
        if 'atk_max' in delta:
            # Ensure atk_max stays strictly >= atk_min + 1 for a valid range
            self.atk_max = max(self.atk_min + 1, self.atk_max + delta['atk_max'])
        if 'crit_chance' in delta:
            # Keep crit chance in a sane range
            self.crit_chance = min(0.8, max(0.0, self.crit_chance + delta['crit_chance']))
    

    def can_use(self, skill) -> bool:
        return self.sp >= skill.cost

    def use_skill(self, skill):
        self.sp -= skill.cost
      


    def to_dict(self) -> dict:
        """
        Convert player's current state to a JSON-serializable dict.
        NOTE: skills are saved by name list.
        """
        return {
            "row": self.row,
            "col": self.col,
            "hp": self.hp,
            "hp_max": self.hp_max,
            "sp": self.sp,
            "sp_max": self.sp_max,
            "atk_min": self.atk_min,
            "atk_max": self.atk_max,
            "level": self.level,
            "exp": self.exp,
            "potions": self.potions,
            "sp_potions": self.sp_potions,
            "crit_chance": getattr(self, "crit_chance", 0.0),
            "skills": [s.name for s in self.skills],  # save by names
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """
        Create a Player from a saved dict.
        Skills are rebuilt by matching names from ALL_SKILLS.
        """
        # The initial position is filled with the saved row/col; the remaining values ​​are filled one by one
        p = cls(row=data.get("row", 1), col=data.get("col", 1))
        p.hp = data["hp"]; p.hp_max = data["hp_max"]
        p.sp = data["sp"]; p.sp_max = data["sp_max"]
        p.atk_min = data["atk_min"]; p.atk_max = data["atk_max"]
        p.level = data["level"]; p.exp = data["exp"]
        p.potions = data.get("potions", 0)
        p.sp_potions = data.get("sp_potions", 0)
        p.crit_chance = data.get("crit_chance", 0.0)

        # Rebuild skills: match by name from ALL_SKILLS (ignore if not found)
        names = data.get("skills", [])
        name2skill = {s.name: s for s in ALL_SKILLS}
        p.skills = [name2skill[n] for n in names if n in name2skill]
        return p
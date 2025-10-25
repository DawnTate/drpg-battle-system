# monsters.py
# Monster templates + spawning logic
from dataclasses import dataclass
import random
from typing import List, Dict, Tuple

@dataclass
class Monster:
    name: str
    level: int
    hp: int
    atk_min: int
    atk_max: int
    elite: bool = False

    def is_alive(self) -> bool:
        return self.hp > 0

# Monster database (extend freely)
MONSTER_DB: List[Dict] = [
    {"name": "Cute Slime",     "base_hp": 6,  "base_atk_min": 1, "base_atk_max": 3, "floors": [1,2],     "weight": 5},
    {"name": "Bat Ghost",       "base_hp": 7,  "base_atk_min": 1, "base_atk_max": 4, "floors": [1,2,3],  "weight": 4},
    {"name": "Skeleton",  "base_hp": 10, "base_atk_min": 2, "base_atk_max": 5, "floors": [2,3,4],  "weight": 4},
    {"name": "Huge Goblin",    "base_hp": 12, "base_atk_min": 2, "base_atk_max": 6, "floors": [3,4,5],  "weight": 3},
    {"name": "Specter",     "base_hp": 14, "base_atk_min": 3, "base_atk_max": 7, "floors": [4,5],    "weight": 2},
]

# Elite tuning
ELITE_CHANCE  = 0.4
ELITE_HP_MULT = 1.35
ELITE_ATK_MULT = 1.25

def _weighted_choice(items: List[Dict], weights: List[float]) -> Dict:
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0.0
    for item, w in zip(items, weights):
        if upto + w >= r:
            return item
        upto += w
    return items[-1]

def _pick_template_for_floor(floor: int) -> Dict:
    """select which monster will appear"""
    pool = [m for m in MONSTER_DB if floor in m["floors"]]
    if not pool:
        pool = MONSTER_DB
    return _weighted_choice(pool, [m["weight"] for m in pool])

def _scale_stats(tpl: Dict, level: int, elite: bool) -> Tuple[int, int, int]:
    """Linear scaling; elites get multiplicative boosts."""
    hp  = tpl["base_hp"] + 4 * level
    a1  = tpl["base_atk_min"] + max(0, level - 1)
    a2  = tpl["base_atk_max"] + 2 * level
    if elite:
        hp = int(hp * ELITE_HP_MULT)
        a1 = max(1, int(a1 * ELITE_ATK_MULT))
        a2 = max(a1 + 1, int(a2 * ELITE_ATK_MULT))
    return hp, a1, a2

def generate_monster(floor: int) -> Monster:
    """
    Choose template by floor, roll level (floor~floor+1), maybe elite,
    return a scaled Monster instance.
    """
    tpl = _pick_template_for_floor(floor)
    level = random.randint(max(1, floor), max(1, floor + 1))
    elite = (random.random() < ELITE_CHANCE)
    hp, a1, a2 = _scale_stats(tpl, level, elite)
    return Monster(name=tpl["name"], level=level, hp=hp, atk_min=a1, atk_max=a2, elite=elite)


def generate_mimic_monster(floor: int) -> Monster:
    """
    Always generate an elite monster (Mimic chest monster).
    Stronger than normal encounters, but uses same floor templates.
    """
    tpl = _pick_template_for_floor(floor)
    level = random.randint(max(1, floor), max(1, floor + 1))

    # Force elite = True
    elite = True

    # Scale stats with elite multipliers
    hp, a1, a2 = _scale_stats(tpl, level, elite)

    # Append '(Mimic)' to monster name for clarity
    return Monster(
        name=f"{tpl['name']} Mimic",
        level=level,
        hp=hp,
        atk_min=a1,
        atk_max=a2,
        elite=elite
    )

"""
Chest event handler:
- When stepping on a chest ('C'), there is a configured chance to spawn a Mimic (elite).
- If not a Mimic, the player chooses:
  1) restore % of HP & SP now, or
  2) gamble for permanent random stat changes (each may backfire).
Config values are loaded from config.json via config.CFG.
"""

import random
from config import CFG
from battle import battle
from monsters import generate_mimic_monster  
from battle import wait_for_key, cls

def chest_event(player, floor: int, grid, r: int, c: int):
    """
    Resolve an interaction with a chest at (r, c).
    Returns a pair: (message: str, consumed: bool)
      - consumed=True means the chest tile becomes '.'.
      - consumed=False keeps the chest (e.g., player escaped the Mimic).
    """
    T = CFG["treasure"]

    # 1) Chance to be a Mimic (elite monster)
    if random.random() < float(T["mimic_chance"]):
        cls()
        print("The chest was a Mimic!")
        monster = generate_mimic_monster(floor)
        outcome = battle(player, monster)   # "win" | "lose" | "escape"

        if outcome == "lose":
            return "You were defeated by the Mimic.", False
        if outcome == "escape":
            # Keep the chest for later; player can try again next time.
            return "You escaped from the Mimic. The chest remains...", False

        # Win reward: heal and permanent boosts (bias towards positive)
        player.heal_percent(float(T["heal_rate"]))
        boosts = _roll_permanent_boosts(is_mimic=True)
        _apply_and_print_boosts(player, boosts)
        grid[r][c] = '.'
        return "You defeated the Mimic and feel empowered!", True

    # 2) Normal chest: give the player a choice
    cls()
    print("You found a chest! Choose one:")
    print(f"1) Restore {int(float(T['heal_rate']) * 100)}% HP & SP now")
    print("2) Gamble: permanent random stat boosts (each pick may backfire)")

    choice = input("Select [1/2] > ").strip()
    if choice == "1":
        player.heal_percent(float(T["heal_rate"]))
        grid[r][c] = '.'
        return "You feel refreshed.", True

    # Choice 2: gamble with possible backlash per-attribute
    boosts = _roll_permanent_boosts(is_mimic=False)
    _apply_and_print_boosts(player, boosts)
    grid[r][c] = '.'
    return "You opened the chest and accepted its fate.", True


def _roll_permanent_boosts(is_mimic: bool) -> dict:
    """
    Decide which attributes to change and by how much.
    - When 'is_mimic' is True: always positive and slightly stronger (bias).
    - Otherwise: each affected attribute can backfire (negative) with a given probability.
    """
    T = CFG["treasure"]
    kmin = int(T["gamble_attr_count_min"])
    kmax = int(T["gamble_attr_count_max"])
    backfire = float(T["backfire_prob"])
    bias = float(T["mimic_boost_bias"]) if is_mimic else 0.0

    candidates = ['hp_max', 'sp_max', 'atk_min', 'atk_max', 'crit_chance']
    k = random.randint(kmin, kmax)
    picks = random.sample(candidates, k)
    delta = {}

    for key in picks:
        if key == 'hp_max':
            base = random.randint(3, 7)
            base = int(base * (1.0 + bias))
            sign = +1 if (is_mimic or random.random() > backfire) else -1
            delta[key] = sign * base

        elif key == 'sp_max':
            base = random.randint(2, 5)
            base = int(base * (1.0 + bias))
            sign = +1 if (is_mimic or random.random() > backfire) else -1
            delta[key] = sign * base

        elif key == 'atk_min':
            base = random.choice([1, 2])
            base = max(1, int(base * (1.0 + bias)))
            sign = +1 if (is_mimic or random.random() > backfire) else -1
            delta[key] = sign * base

        elif key == 'atk_max':
            base = random.choice([1, 2, 3])
            base = max(1, int(base * (1.0 + bias)))
            sign = +1 if (is_mimic or random.random() > backfire) else -1
            delta[key] = sign * base

        elif key == 'crit_chance':
            base = 0.02 * (1.0 + bias)   # ±2% (scaled)
            sign = +1 if (is_mimic or random.random() > backfire) else -1
            delta[key] = sign * base

    return delta


def _apply_and_print_boosts(player, boosts: dict) -> None:
    """Apply boosts to player and print a compact, readable summary."""
    if not boosts:
        print("Nothing happens...")
        wait_for_key()
        return

    player.apply_permanent_boosts(boosts)
    parts = []
    for k, v in boosts.items():
        if k == 'crit_chance':
            parts.append(f"{k} {'+' if v>=0 else ''}{int(v*100)}%")
        else:
            parts.append(f"{k} {'+' if v>=0 else ''}{v}")
    print("Permanent change:", ", ".join(parts))
    wait_for_key()


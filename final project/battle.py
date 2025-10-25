import os
import time
import random
from models import Player
from monsters import Monster, generate_monster  # ← use shared monster module

# ---------- Terminal FX helpers (visual effects for battles) ----------
try:
    from colorama import init, Fore, Style
    init()
    HAS_COLOR = True
except Exception:
    HAS_COLOR = False
    class _Dummy: RESET = ""; BRIGHT = ""; RED = ""; YELLOW = ""; CYAN = ""
    Fore = Style = _Dummy()  # type: ignore

def cls():
    """Clear the console screen (Windows/Linux/Mac)."""
    os.system("cls" if os.name == "nt" else "clear")

def typeout(text: str, delay: float = 0.012):
    """Typewriter effect for tension."""
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()

def flash_banner(text: str):
    """Big highlighted banner (critical, warnings, etc.)."""
    line = "=" * max(24, len(text) + 6)
    if HAS_COLOR:
        print(Fore.YELLOW + Style.BRIGHT + line + Style.RESET_ALL)
        print(Fore.RED + Style.BRIGHT + f"   {text}   " + Style.RESET_ALL)
        print(Fore.YELLOW + Style.BRIGHT + line + Style.RESET_ALL)
    else:
        print(line); print(f"   {text}   "); print(line)

def hit_stop(duration: float = 0.08):
    """Short pause to sell impact."""
    time.sleep(duration)

def screen_shake(frames: int = 6, spread: int = 6, message: str = "!!! CRITICAL HIT !!!"):
    """Clear-screen shake with random horizontal jitter."""
    for _ in range(frames):
        cls()
        offset = " " * random.randint(0, spread)
        if HAS_COLOR:
            print(offset + Fore.RED + Style.BRIGHT + message + Style.RESET_ALL)
        else:
            print(offset + message)
        time.sleep(0.045)

def wait_for_key(msg: str = "Press Enter to continue..."):
    """Keep FX on screen until player confirms."""
    try:
        prompt = msg
        if HAS_COLOR:
            prompt = Fore.CYAN + msg + Style.RESET_ALL
        input("\n" + prompt)
    except EOFError:
        time.sleep(0.6)

# ---------- Battle loop ----------
def battle(player: Player, monster: Monster) -> str:
    """
    Turn-based battle.
    Returns: "win" | "lose" | "escape".
    - Critical hits stun the monster for 1 turn.
    """
    # Spawn line with name + elite highlight
    mname = f"Elite {monster.name}" if getattr(monster, "elite", False) else monster.name
    if HAS_COLOR and getattr(monster, "elite", False):
        mname = Fore.YELLOW + Style.BRIGHT + mname + Style.RESET_ALL
    cls()
    print(f"A wild {mname} (Lv {monster.level}) appeared! HP={monster.hp}")

    monster_stun = 0  # stunned turns

    while monster.is_alive() and player.is_alive():
        print()
        action = input("Choose action: [A]ttack, [S]kill, [H]eal, [P]otion(SP), [I]nformation, [R]un > ").strip().lower()
        print()

        # Attack
        if action == "a":
            dmg, is_crit = player.roll_damage()
            monster.hp -= dmg
            if is_crit:
                monster_stun = 1
                hit_stop(min(0.04 + dmg * 0.003, 0.18))
                screen_shake(frames=6, spread=6, message="!!! CRITICAL HIT !!!")
                flash_banner("CRITICAL! MONSTER IS KNOCKED DOWN!")
                print(f"You deal {dmg} critical damage. ({monster.name} HP={max(monster.hp,0)})")
            else:
                print(f"You hit the {monster.name} for {dmg} damage. ({monster.name} HP={max(monster.hp,0)})")

        # Heal
        elif action == "h":
            if player.potions > 0:
                heal = 10
                player.hp = min(player.hp + heal, player.hp_max)
                player.potions -= 1
                print(f"You used a potion and recovered {heal} HP. (Player HP={player.hp}) (HP potion left: {player.potions})")
            else:
                print("No potions left!")
        
        #Potion (sp)
        elif action == "p":
            if player.sp_potions > 0:
                restore = 6  # restore 6 sp 
                player.sp = min(player.sp + restore, player.sp_max)
                player.sp_potions -= 1
                print(f"You used one SP potion and restored {restore} SP. (SP={player.sp}/{player.sp_max}) (SP potion left: {player.sp_potions})")
            else:
                print("No SP potions left!")

        # Information
        elif action == "i":
            print(f'Your hp: {player.hp}/{player.hp_max}')
            print(f'Your sp: {player.sp}/{player.sp_max}')
            print(f'You now have {player.potions} hp potions.')
            print(f'You now have {player.sp_potions} sp potions.')

            continue


        # Run
        elif action == "r":
            if random.random() < 0.5:
                print("You escaped successfully!")
                return "escape"
            else:
                print("Escape failed!")
        
        # Skills
        elif action == "s":
            print("== Skills ==")
            for idx, sk in enumerate(player.skills, 1):
                print(f"{idx}) {sk.name}  Cost:{sk.cost} SP  Mult:{sk.multiplier}x  - {sk.desc}")
            print("0) Cancel")
            print()

            sel = input("Select skill number > ").strip()
            if not sel.isdigit():
                print("Invalid input."); continue
            sel = int(sel)
            if sel == 0:
                continue
            if not (1 <= sel <= len(player.skills)):
                print("Invalid selection."); continue

            sk = player.skills[sel-1]
            if not player.can_use(sk):
                print("Not enough SP!"); continue

            # damage = base attack * skill mutiplier
            base_dmg, is_crit = player.roll_damage()
            dmg = int(base_dmg * sk.multiplier)
            monster.hp -= dmg
            player.use_skill(sk)

            if is_crit:
                monster_stun = 1  # same as basic attack crit
                hit_stop(min(0.04 + dmg * 0.003, 0.18))  # pause for tension
                screen_shake(frames=6, spread=6, message="!!! CRITICAL SKILL HIT !!!")
                flash_banner(f"CRITICAL! {monster.name} IS KNOCKED DOWN!")
                print(f"You used {sk.name} and dealt {dmg} CRITICAL damage! ({monster.name} HP={max(monster.hp,0)})")
            else:
                print()
                print(f"You used {sk.name} and dealt {dmg} damage. ({monster.name} HP={max(monster.hp,0)})")
            # --- Skill's own stun (independent of crit) ---
            # Apply only if the monster survived the hit.
            if sk.stun and monster.hp > 0:
                monster_stun = 1
                print(f"The {monster.name} is stunned by {sk.name}!")

        else:
            print("Invalid action.")
            continue

        # Monster turn (skipped if stunned or dead)
        if monster.is_alive():
            if monster_stun > 0:
                print(f"The {monster.name} is stunned and cannot act this turn!")
                monster_stun -= 1
            else:
                mdmg = random.randint(monster.atk_min, monster.atk_max)
                player.hp -= mdmg
                print(f"The {monster.name} hits you for {mdmg} damage. (Player HP={max(player.hp,0)})")

    # Outcome
    if not player.is_alive():
        print("You were defeated...")
        wait_for_key()
        return "lose"
    else:
        base_exp = 3 + monster.level * 2
        if getattr(monster, "elite", False):
            base_exp = int(base_exp * 1.6)
        player.gain_exp(base_exp)
        print(f"You defeated the {monster.name}! +{base_exp} EXP.")
        wait_for_key()
        return "win"

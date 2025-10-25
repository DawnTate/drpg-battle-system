
"""
Simple JSON-based save/load utilities.
We save: floor number, player snapshot, current grid (map).
"""

import json
import os
from typing import Optional, Tuple, List
from models import Player

SAVE_PATH = "save.json"

def save_game(player: Player, floor: int, grid: List[List[str]], path: str = SAVE_PATH) -> None:
    """
    Serialize the current game state into a JSON file.
    """
    data = {
        "floor": floor,
        "player": player.to_dict(),
        "grid": grid,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[Save] Game saved to {os.path.abspath(path)}")

def load_game(path: str = SAVE_PATH) -> Optional[Tuple[Player, int, List[List[str]]]]:
    """
    Load the game state from a JSON file.
    Returns (player, floor, grid) or None if file missing/invalid.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        player = Player.from_dict(data["player"])
        floor = int(data["floor"])
        grid = data["grid"]
        # Basic checks
        if not isinstance(grid, list) or not grid or not isinstance(grid[0], list):
            raise ValueError("Invalid grid in save file.")
        return player, floor, grid
    except FileNotFoundError:
        print("[Load] No save file found.")
        return None
    except Exception as e:
        print(f"[Load] Failed to load save: {e}")
        return None

def has_save(path: str = SAVE_PATH) -> bool:
    """Quick existence check."""
    return os.path.exists(path)

def delete_save(path: str = SAVE_PATH) -> None:
    """clear save"""
    try:
        os.remove(path)
        print("[Save] Save file deleted.")
    except FileNotFoundError:
        pass

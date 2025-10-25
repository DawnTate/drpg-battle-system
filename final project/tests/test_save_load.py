
"""
Round-trip tests for File I/O save/load.

We write a temporary save file, load it back, and verify core fields.

"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tempfile
import unittest

from models import Player
from world import load_floor, choose_spawn
from save_load import save_game, load_game


class TestSaveLoad(unittest.TestCase):
    def test_save_and_load_roundtrip(self):
        # --- Prepare a small realistic snapshot ---
        floor = 2
        grid = load_floor(floor)
        player = Player(row=1, col=1)
        player.row, player.col = choose_spawn(grid)
        player.hp = 17
        player.sp = 8
        player.level = 3
        player.exp = 12

        # --- Save to a temporary file ---
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tmp_path = tf.name
        try:
            save_game(player, floor, grid, path=tmp_path)
            loaded = load_game(path=tmp_path)  # expected -> (Player, int, grid)
            self.assertIsNotNone(loaded)

            p2, f2, g2 = loaded
            # --- Verify key values survived the round-trip ---
            self.assertEqual(f2, floor)
            self.assertEqual((p2.row, p2.col), (player.row, player.col))
            self.assertEqual(p2.hp, player.hp)
            self.assertEqual(p2.sp, player.sp)
            self.assertEqual(p2.level, player.level)
            self.assertEqual(p2.exp, player.exp)
            self.assertEqual(len(g2), len(grid))
            self.assertEqual(len(g2[0]), len(grid[0]))
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    def test_load_nonexistent_file(self):
        """Loading a non-existent save file should return None or raise error."""
        loaded = load_game(path="nonexistent_file.json")
        self.assertIsNone(loaded)  


if __name__ == "__main__":
    unittest.main()

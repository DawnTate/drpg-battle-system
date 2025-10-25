# tests/test_chest.py
"""
Tests for chest interactions:
1) A normal chest where the player chooses to heal.
2) A Mimic chest encounter with a forced successful escape.

We temporarily modify CFG["treasure"] values and restore them afterwards,
so normal gameplay settings are unaffected.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import unittest
from unittest.mock import patch
from copy import deepcopy

from models import Player
from events import chest_event
from world import CHEST_TILE
from config import CFG


class TestChestEvent(unittest.TestCase):
    def setUp(self):
        # Minimal 3x3 map with a chest at the center.
        self.grid = [
            ["#", "#", "#"],
            ["#", CHEST_TILE, "#"],
            ["#", "#", "#"],
        ]
        self.r, self.c = 1, 1
        self.player = Player(row=1, col=1)

    def test_normal_chest_heal_choice(self):
        """
        Force a normal chest (no Mimic) and select option '1' (heal 30%).
        The chest should be consumed (tile turns to '.') and a message returned.
        """
        old_cfg = deepcopy(CFG["treasure"])
        try:
            CFG["treasure"]["mimic_chance"] = 0.0  # ensure no Mimic
            CFG["treasure"]["heal_rate"] = 0.30

            with patch("builtins.input", return_value="1"):
                msg, consumed = chest_event(self.player, floor=1, grid=self.grid, r=self.r, c=self.c)

            self.assertTrue(consumed)
            self.assertEqual(self.grid[self.r][self.c], ".")
            self.assertIsInstance(msg, str)
            self.assertTrue(len(msg) > 0)
        finally:
            CFG["treasure"] = old_cfg  # restore original settings

    @patch("time.sleep", lambda *_: None)  # speed up any battle FX
    def test_mimic_chest_escape_success(self):
        """
        Force a Mimic (treasure monster) and make escape guaranteed.
        After a successful escape, the chest should remain (not consumed).
        """
        old_cfg = deepcopy(CFG["treasure"])
        try:
            CFG["treasure"]["mimic_chance"] = 1.0  # always Mimic

            with patch("builtins.input", side_effect=["r"]), \
                 patch("random.random", return_value=0.0):
                msg, consumed = chest_event(self.player, floor=1, grid=self.grid, r=self.r, c=self.c)

            self.assertFalse(consumed)
            self.assertEqual(self.grid[self.r][self.c], CHEST_TILE)
            self.assertIn("escape", msg.lower())
        finally:
            CFG["treasure"] = old_cfg


if __name__ == "__main__":
    unittest.main()

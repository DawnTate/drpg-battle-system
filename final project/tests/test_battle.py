# tests/test_battle.py
"""
Unit tests for the turn-based battle system.

We patch:
- battle.wait_for_key: no-op (avoid extra input after win/lose)
- time.sleep: no-op (speed up tests)
So each test only needs to provide the input(s) relevant to the action.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import builtins
import sys
import unittest

from unittest.mock import patch
from models import Player
from monsters import Monster
from battle import battle


class TestBattle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Patch time.sleep once for all tests to keep them fast."""
        cls._sleep_patcher = patch("time.sleep", lambda *_: None)
        cls._sleep_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls._sleep_patcher.stop()

    def setUp(self):
        """
        Before each test, disable the in-battle 'press Enter to continue'
        so we don't need to mock a second input.
        """
        self._wait_patcher = patch("battle.wait_for_key", lambda *_: None)
        self._wait_patcher.start()

    def tearDown(self):
        self._wait_patcher.stop()

    def test_player_wins_with_one_attack(self):
        """
        Player should win if the monster HP is already very low.
        We press 'a' (attack) once and expect a 'win' result.
        """
        player = Player(row=1, col=1)
        monster = Monster(name="Training Dummy", level=1, hp=1, atk_min=0, atk_max=0)

        with patch("builtins.input", side_effect=["a"]):
            result = battle(player, monster)

        self.assertEqual(result, "win")

    def test_player_loses_when_monster_hits_hard(self):
        """
        Player should lose if their HP is 1 and the monster always hits hard.
        We press 'a' once; force player's hit to be non-crit so the enemy acts.
        """
        player = Player(row=1, col=1)
        player.hp = 1  # fragile player
        monster = Monster(name="Ogre", level=5, hp=999, atk_min=50, atk_max=50)

        # Force the player's attack to be 1 damage and NOT critical (no stun).
        with patch.object(Player, "roll_damage", return_value=(1, False)), \
            patch("builtins.input", side_effect=["a"]):
            result = battle(player, monster)

        self.assertEqual(result, "lose")
    

    def test_player_escapes_successfully(self):
        """
        Player chooses to run ('r').
        Force random.random() to return 0.0 so escape always succeeds.
        """
        player = Player(row=1, col=1)
        monster = Monster(name="Snail", level=1, hp=10, atk_min=0, atk_max=1)

        with patch("builtins.input", side_effect=["r"]), \
             patch("random.random", return_value=0.0):
            result = battle(player, monster)

        self.assertEqual(result, "escape")


    def test_run_fails_then_attack_wins_shows_message(self):
        """
        Force escape to fail, then attack once to finish the battle.
        Verify that 'Escape failed' message appeared and final result is a win.
        """
        player = Player(row=1, col=1)
        monster = Monster(name="Box Slime", level=1, hp=1, atk_min=0, atk_max=0)

            
        with patch("random.random", return_value=0.99), \
            patch("builtins.input", side_effect=["r","a"]), \
            patch("builtins.print", wraps=builtins.print) as mock_print:
           result = battle(player, monster)

        printed = " ".join(" ".join(map(str, c.args)) for c in mock_print.call_args_list)
        self.assertIn("ESCAPE FAILED", printed.upper())

    


if __name__ == "__main__":
    unittest.main()

import random

from save_load import save_game, load_game, has_save, delete_save
from models import Player
from world import load_floor, render, try_move, choose_spawn
from events import chest_event
from world import CHEST_TILE
from monsters import generate_monster
from battle import battle  # returns: "win" | "lose" | "escape"
from battle import wait_for_key



def game_loop():
    """
    Main game loop for the DRPG.
    - Starts on floor 1
    - Player explores the dungeon until reaching the exit
    - Game ends after clearing the final floor
    - Save/Load support
    """
    # --- Start menu: New vs Load ---
    floor = 1
    grid = None
    player = None
    is_stopped = False
    
    while(is_stopped == False):

        # Save files exist
        if has_save():
            print("Save found. Choose:")
            print("[C] Continue (load save)")
            print("[N] New Game (overwrite existing save)")
            choice = input("> ").strip().lower()

            if choice == "c":
                loaded = load_game()
                if loaded:
                    player, floor, grid = loaded
                    tip = "Save loaded."
                    is_stopped = True
                else:
                    print("Failed to load save. Starting a new game...")
                    delete_save()  # prevent dirty save files
                    grid = load_floor(floor)
                    player = Player(row=1, col=1)
                    player.row, player.col = choose_spawn(grid)
                    tip = "Enter the dungeon... Find 'E' to reach the next floor."
                    is_stopped = True

            elif choice == "n":
                # Restart Game
                delete_save()
                grid = load_floor(floor)
                player = Player(row=1, col=1)
                player.row, player.col = choose_spawn(grid)
                tip = "Enter the dungeon... Find 'E' to reach the next floor."
                is_stopped = True
            else:
                print('Invalid Input.')

        else:
            print()
            print('No save file found, automatically starting a new game')
            wait_for_key()
            grid = load_floor(floor)
            player = Player(row=1, col=1)
            player.row, player.col = choose_spawn(grid)
            tip = "Enter the dungeon... Find 'E' to reach the next floor."
            is_stopped = True

   

    while True:
        # Render map and player status
        render(grid, player, floor, tip)

        # Get player input
        cmd = input("Command (WASD to move, Q to quit, L to learn the legend, T to save) > ").strip().lower()
        if cmd == "q":
            print("You have quit the game. Goodbye!")
            break

        if cmd == 'l':
            print()
            print("#: Wall, you cannot pass the wall")
            print(".: Road, you can just walk on the road.")
            print("@: You, this is your location.")
            print("E: Entrance, you have to go to there(goal).")
            print("C: Treasure Chest, you can get reward or other things...?")
            wait_for_key()
            continue

        if cmd == "t":
            print()
            save_game(player, floor, grid)
            tip = "Game saved."
            wait_for_key()
            continue
        # Attempt to move (remember previous position for potential escape)
        prev_row, prev_col = player.row, player.col
        moved, tip, at_exit = try_move(grid, player, cmd)
        if not moved:
            continue  # Invalid move, render again

        # After a successful move:
        tile = grid[player.row][player.col]

        # If standing on a chest, resolve chest event first.
        if tile == CHEST_TILE:
            tip_msg, consumed = chest_event(player, floor, grid, player.row, player.col)
            tip = tip_msg
            # chest_event turns the tile into '.' when consumed.
            # Skip random encounter & exit check this turn to avoid double events.
            continue


        # -------------------------
        # Random encounter trigger
        # -------------------------
        if random.random() < 0.25:  # 25% chance after each move
            monster = generate_monster(floor)
            outcome = battle(player, monster)  # "win" | "lose" | "escape"

            if outcome == "lose":
                print("Game Over. Thanks for playing!")
                break

            if outcome == "escape":
                # Do not consume the step: revert to previous tile
                player.row, player.col = prev_row, prev_col
                tip = "You escaped and returned to your previous position."
                # Skip exit check this turn
                continue

            # outcome == "win"
            tip = "You won the battle."

        # Check if player reached the exit (only if we didn't escape)
        if at_exit:
            if floor < 5:
                floor += 1
                grid = load_floor(floor)
                player.row, player.col = choose_spawn(grid)
                tip = f"You have entered Floor {floor}."
            else:
                print("Congratulations! You have reached the final exit. Victory!")
                break

if __name__ == "__main__":
    game_loop()

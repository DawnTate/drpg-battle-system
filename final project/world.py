import random
from typing import List, Tuple
from models import Player
from config import CFG




# =========================
# Configuration
# =========================
CHEST_TILE = "C"  # tile used to draw a chest
CHEST_COUNT = int(CFG["treasure"]["chest_per_floor"])


MAP_W, MAP_H = 11, 11  # Use odd numbers for cleaner maze layout

# Movement directions for WASD
DIRS = {
    "w": (-1, 0),
    "s": ( 1, 0),
    "a": ( 0,-1),
    "d": ( 0, 1),
}

# =========================
# Maze Generation
# =========================
def _blank_grid(w: int, h: int, fill: str = "#") -> List[List[str]]:
    """Create a grid filled with a single character (default: walls)."""
    return [[fill for _ in range(w)] for _ in range(h)]

def _in_bounds(g: List[List[str]], r: int, c: int) -> bool:
    """Check if (r,c) is inside the grid."""
    return 0 <= r < len(g) and 0 <= c < len(g[0])

def _neighbors_2step(r: int, c: int) -> List[Tuple[int,int]]:
    """Return cells 2 steps away (used for DFS maze carving)."""
    return [(r-2,c), (r+2,c), (r,c-2), (r,c+2)]

def _carve_maze(w: int, h: int) -> List[List[str]]:
    """Generate a random maze using recursive backtracking (DFS)."""
    g = _blank_grid(w, h, "#")
    sr = random.randrange(1, h, 2)
    sc = random.randrange(1, w, 2)
    g[sr][sc] = "."
    stack = [(sr, sc)]

    while stack:
        r, c = stack[-1]
        nbrs = [(nr, nc) for nr, nc in _neighbors_2step(r, c)
                if _in_bounds(g, nr, nc) and g[nr][nc] == "#"]
        random.shuffle(nbrs)
        if not nbrs:
            stack.pop()
            continue
        nr, nc = nbrs.pop()
        mr, mc = (r + nr)//2, (c + nc)//2
        g[mr][mc] = "."
        g[nr][nc] = "."
        stack.append((nr, nc))
    return g

def _random_free_cell(g: List[List[str]]) -> Tuple[int,int]:
    """Pick a random floor cell ('.') as players' start point."""
    free = [(r,c) for r in range(1, len(g)-1)
                  for c in range(1, len(g[0])-1)
                  if g[r][c] == "."]
    return random.choice(free)

def _farthest_from(g: List[List[str]], start: Tuple[int,int]) -> Tuple[int,int]:
    """Find the farthest reachable cell from start using BFS."""
    from collections import deque
    h, w = len(g), len(g[0])
    sr, sc = start
    dist = [[-1]*w for _ in range(h)]
    dq = deque([(sr,sc)])
    dist[sr][sc] = 0
    far = (sr, sc)
    while dq:
        r,c = dq.popleft()
        if dist[r][c] > dist[far[0]][far[1]]:
            far = (r,c)
        for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if _in_bounds(g,nr,nc) and g[nr][nc] == "." and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                dq.append((nr,nc))
    return far

def _place_exit_on_edge(g: List[List[str]], from_cell: Tuple[int,int]) -> Tuple[int,int]:
    """Place exit 'E' on the farthest edge cell from spawn."""
    h, w = len(g), len(g[0])
    far_r, far_c = _farthest_from(g, from_cell)
    candidates = []
    for c in range(1, w-1):
        if g[1][c] == ".":     candidates.append((1,c))
        if g[h-2][c] == ".":   candidates.append((h-2,c))
    for r in range(1, h-1):
        if g[r][1] == ".":     candidates.append((r,1))
        if g[r][w-2] == ".":   candidates.append((r,w-2))
    if candidates:
        candidates.sort(key=lambda rc: abs(rc[0]-far_r)+abs(rc[1]-far_c), reverse=True)
        er, ec = candidates[0]
    else:
        er, ec = far_r, far_c
    g[er][ec] = "E"
    return (er, ec)

def _place_chests(grid, n: int, forbidden: set[tuple[int, int]] | None = None) -> None:
    """
    Randomly place n chests ('C') on walkable tiles ('.').
    - Skips any coordinates listed in `forbidden` (e.g., spawn, exit).
    - Uses a simple retry loop with an upper bound to avoid infinite loops.
    """
    import random
    h, w = len(grid), len(grid[0])
    placed, tries = 0, 0
    forbidden = forbidden or set()

    while placed < n and tries < 300:
        tries += 1
        r = random.randint(1, h - 2)
        c = random.randint(1, w - 2)

        # Must be floor, not a wall, not an exit, and not forbidden
        if grid[r][c] != ".": 
            continue
        if (r, c) in forbidden:
            continue

        grid[r][c] = CHEST_TILE
        placed += 1


# =========================
# Public API
# =========================
def load_floor(floor: int, seed: int | None = None) -> List[List[str]]:
    """
    Generate a floor:
    - A random DFS maze
    - Player spawn at random floor cell
    - Exit placed on far edge
    """
    if seed is not None:
        random.seed(seed)
    g = _carve_maze(MAP_W, MAP_H)
    return g


def choose_spawn(g: List[List[str]]) -> Tuple[int,int]:
    """Choose a random spawn and place exit far from it."""
    spawn = _random_free_cell(g)
    _place_exit_on_edge(g, spawn)

    # --- place chests after spawn/exit are decided, avoid the spawn tile ---
    _place_chests(g, CHEST_COUNT, forbidden={spawn})

    return spawn
    

def render(grid: List[List[str]], player: Player, floor: int, msg: str="") -> None:
    """Render the map with player and status info."""
    g = [row[:] for row in grid]
    g[player.row][player.col] = "@"
    print("\n".join("".join(row) for row in g))
    print("-" * len(g[0]))
    print(f"Floor {floor} | HP {player.hp}/{player.hp_max} | SP {player.sp}/{player.sp_max} | ATK {player.atk_min}-{player.atk_max} | Crit {player.crit_chance:.2f}| LV {player.level} EXP {player.exp}/{player.exp_to_next()}")
    if msg: print(msg)
    print("[WASD] move  [Q] quit  [L] legend [T] Save")


def try_move(grid: List[List[str]], player: Player, cmd: str) -> Tuple[bool,str,bool]:
    """
    Try to move player based on input command.
    Returns: (moved?, message, reached_exit?)
    """
    if cmd not in DIRS:
        return False, "Invalid command.", False
    dr, dc = DIRS[cmd]
    nr, nc = player.row + dr, player.col + dc
    if not _in_bounds(grid, nr, nc) or grid[nr][nc] == "#":
        return False, "You hit a wall.", False
    player.row, player.col = nr, nc
    return True, "You moved one step.", (grid[nr][nc] == "E")

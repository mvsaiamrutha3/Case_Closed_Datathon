#!/usr/bin/env python3
"""
board.py
---------
Provides grid and movement utilities for the Case Closed arena.
Compatible with heuristic.py and RL environments.
"""

from typing import List, Tuple
from functools import lru_cache

# Arena size
H, W = 18, 20

# Directions and deltas
DIRS = ("UP", "DOWN", "LEFT", "RIGHT")
DELTAS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}

# ------------------------------------------------------------
# Core utilities
# ------------------------------------------------------------
def inb(r: int, c: int) -> bool:
    """Check if coordinates are within arena bounds."""
    return 0 <= r < H and 0 <= c < W


def neighbors(r: int, c: int) -> List[Tuple[int, int]]:
    """Return list of neighboring coordinates (4-connected)."""
    out = []
    for d in DIRS:
        dr, dc = DELTAS[d]
        nr, nc = r + dr, c + dc
        if inb(nr, nc):
            out.append((nr, nc))
    return out


def legal_moves(board: List[List[str]], pos: Tuple[int, int]) -> List[str]:
    """
    Return all legal directions from the given position,
    i.e., directions that do not crash into walls or go out of bounds.
    """
    r, c = pos
    moves = []
    for d in DIRS:
        dr, dc = DELTAS[d]
        nr, nc = r + dr, c + dc
        if inb(nr, nc) and board[nr][nc] == " ":
            moves.append(d)
    return moves


# ------------------------------------------------------------
# Flood fill for space evaluation
# ------------------------------------------------------------
@lru_cache(maxsize=512)
def flood_fill_area(board_tuple: Tuple[Tuple[str, ...], ...], start: Tuple[int, int]) -> int:
    """
    Compute the number of reachable open cells from a position using DFS.
    Cached for efficiency when evaluating many moves on the same board.
    """
    Hh, Ww = len(board_tuple), len(board_tuple[0])
    if not inb(*start) or board_tuple[start[0]][start[1]] != " ":
        return 0

    seen = {start}
    stack = [start]
    while stack:
        r, c = stack.pop()
        for d in DIRS:
            dr, dc = DELTAS[d]
            nr, nc = r + dr, c + dc
            if (nr, nc) not in seen and inb(nr, nc) and board_tuple[nr][nc] == " ":
                seen.add((nr, nc))
                stack.append((nr, nc))
    return len(seen)


def to_tuple_board(board: List[List[str]]) -> Tuple[Tuple[str, ...], ...]:
    """Convert board (list of lists) to an immutable tuple version for caching."""
    return tuple(tuple(row) for row in board)

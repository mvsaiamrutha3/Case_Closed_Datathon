#!/usr/bin/env python3
"""
search.py
----------
Move-selection logic for Case Closed heuristic agent.
Evaluates each valid move using `heuristic_score()` and returns the best one.
"""

import random
import numpy as np
from heuristic import heuristic_score
from board import DELTAS, inb, H, W

MOVES = ["UP", "DOWN", "LEFT", "RIGHT"]

def is_valid_move(board, pos, move):
    """Check if a move stays in bounds and avoids walls."""
    dr, dc = DELTAS[move]
    nr, nc = pos[0] + dr, pos[1] + dc
    return inb(nr, nc) and board[nr][nc] != "X"

def choose_move(state, deadline=None):
    """
    Evaluate heuristic score for all valid moves and pick the best one.
    Returns the move name (string).
    """
    board = np.array(state["board"], dtype="<U1")
    you = tuple(state["you"])
    valid_moves = [m for m in MOVES if is_valid_move(board, you, m)]

    if not valid_moves:
        return random.choice(MOVES)

    # Score each valid move
    scores = {m: heuristic_score(state, m) for m in valid_moves}
    best_move = max(scores, key=scores.get)
    return best_move

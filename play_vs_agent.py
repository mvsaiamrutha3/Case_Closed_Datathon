#!/usr/bin/env python3
"""
play_vs_agent.py
----------------
Human (Player 🧍) vs Heuristic Agent (🤖 AI) for Case Closed.

Controls:
    W / ↑  → UP
    S / ↓  → DOWN
    A / ←  → LEFT
    D / →  → RIGHT
Press Q to quit anytime.
"""

import time
import random
import numpy as np
import os
from heuristic import heuristic_score
from board import H, W, DELTAS, inb

MOVES = ["UP", "DOWN", "LEFT", "RIGHT"]
EMPTY, WALL = " ", "X"

BLUE = "\033[94m"
RED = "\033[91m"
GRAY = "\033[90m"
RESET = "\033[0m"

# ------------------------------------------------------------
# Utility helpers
# ------------------------------------------------------------
def make_board():
    return [[EMPTY for _ in range(W)] for _ in range(H)]

def print_board(board, human, ai, delay=0.05):
    """Render board with emojis."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * (W * 3))
    for r in range(H):
        row = ""
        for c in range(W):
            if (r, c) == human:
                row += BLUE + "🧍 " + RESET
            elif (r, c) == ai:
                row += RED + "🤖 " + RESET
            elif board[r][c] == WALL:
                row += GRAY + "X  " + RESET
            else:
                row += GRAY + ".  " + RESET
        print(row.rstrip())
    print("=" * (W * 3))

def is_valid_move(board, pos, move):
    dr, dc = DELTAS[move]
    nr, nc = pos[0] + dr, pos[1] + dc
    return inb(nr, nc) and board[nr][nc] != WALL

def move_player(board, pos, move):
    dr, dc = DELTAS[move]
    nr, nc = pos[0] + dr, pos[1] + dc
    if not inb(nr, nc) or board[nr][nc] == WALL:
        return pos, True
    board[pos[0]][pos[1]] = WALL
    return (nr, nc), False

def make_state(board, you, opp, opp_dir="UP"):
    return {
        "you": list(you),
        "opponent": list(opp),
        "board": board,
        "opponent_last_direction": opp_dir,
    }

# ------------------------------------------------------------
# Player input
# ------------------------------------------------------------
def get_player_move():
    """Read player's move via keyboard input."""
    key = input("Your move (W/A/S/D or Q to quit): ").strip().lower()
    mapping = {
        "w": "UP", "a": "LEFT", "s": "DOWN", "d": "RIGHT",
        "up": "UP", "down": "DOWN", "left": "LEFT", "right": "RIGHT"
    }
    if key in ("q", "quit", "exit"):
        print("👋 You quit the game.")
        exit(0)
    return mapping.get(key)

# ------------------------------------------------------------
# Main gameplay
# ------------------------------------------------------------
def main():
    board = make_board()

    # random safe starting positions far apart
    while True:
        human = (random.randint(2, H - 3), random.randint(2, W - 3))
        ai = (random.randint(2, H - 3), random.randint(2, W - 3))
        if abs(human[0] - ai[0]) + abs(human[1] - ai[1]) > 6:
            break

    last_human, last_ai = "UP", "DOWN"
    turn = 1

    print("\n🧍 You (Blue)  vs  🤖 AI (Red)\n")
    time.sleep(1)

    while True:
        print_board(board, human, ai)
        print(f"Turn {turn}\n")

        # --- Human Move ---
        move = None
        while move not in MOVES:
            move = get_player_move()
            if move not in MOVES:
                print("❌ Invalid move. Use W/A/S/D or Q to quit.")

        new_human, crash_human = move_player(board, human, move)

        # --- AI Move ---
        state_ai = make_state(board, ai, new_human, last_human)
        valid_ai_moves = [m for m in MOVES if is_valid_move(board, ai, m)]
        if not valid_ai_moves:
            print("🏆 You win! AI is trapped.")
            break
        ai_move = max(valid_ai_moves, key=lambda m: heuristic_score(state_ai, m))
        new_ai, crash_ai = move_player(board, ai, ai_move)

        # --- Collision checks ---
        if new_human == new_ai and not crash_human and not crash_ai:
            print_board(board, new_human, new_ai)
            print("💥 Head-on collision! Draw.")
            break
        if crash_human and crash_ai:
            print_board(board, human, ai)
            print("💥 Both crashed! Draw.")
            break
        elif crash_human:
            print_board(board, human, ai)
            print("🤖 AI wins! You crashed.")
            break
        elif crash_ai:
            print_board(board, human, ai)
            print("🏆 You win! AI crashed.")
            break

        # --- Update ---
        human, ai = new_human, new_ai
        last_human, last_ai = move, ai_move
        turn += 1

        time.sleep(0.05)

    print("\n🏁 Game Over.\n")

if __name__ == "__main__":
    main()

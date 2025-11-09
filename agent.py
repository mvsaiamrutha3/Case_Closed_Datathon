#!/usr/bin/env python3
"""
agent.py
---------
Heuristic-based autonomous agent for Case Closed.

Reads JSON game state from stdin and prints one of:
"UP", "DOWN", "LEFT", or "RIGHT".

Uses the `choose_move()` function from search.py.
All errors and logs go to stderr so that stdout
remains clean for move communication.
"""

import sys
import json
import time
from search import choose_move

# Per-tick decision budget (ms)
TICK_BUDGET_MS = 40
VALID_MOVES = {"UP", "DOWN", "LEFT", "RIGHT"}


def sanitize_move(move):
    """
    Ensures the returned move is valid.
    Anything else defaults to "UP".
    """
    if isinstance(move, str):
        move = move.strip().upper()
        if move in VALID_MOVES:
            return move
    print(f"⚠️ Invalid move from choose_move(): {repr(move)} — defaulting to UP", file=sys.stderr)
    return "UP"


def main():
    print("🧠 Heuristic Agent ready. Waiting for game state...", file=sys.stderr)

    while True:
        line = sys.stdin.readline()
        if not line:
            break  # end of game stream
        line = line.strip()
        if not line:
            continue

        try:
            state = json.loads(line)
        except json.JSONDecodeError:
            print("⚠️ Invalid JSON received — skipping.", file=sys.stderr)
            continue

        # Optional decision deadline (not enforced)
        _ = time.perf_counter() + (TICK_BUDGET_MS / 1000.0)

        try:
            move = choose_move(state)
        except Exception as e:
            print(f"⚠️ Exception in choose_move(): {e}", file=sys.stderr)
            move = "UP"

        move = sanitize_move(move)
        print(move)
        sys.stdout.flush()

    print("🏁 Agent terminated.", file=sys.stderr)


if __name__ == "__main__":
    main()

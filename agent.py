#!/usr/bin/env python3
"""
agent.py
---------
Heuristic-based autonomous agent for Case Closed.

Reads JSON game state from stdin and prints chosen move ("UP"/"DOWN"/"LEFT"/"RIGHT").
Uses the `choose_move()` function from search.py to decide.
"""

import sys
import json
import time
from search import choose_move

# Per-tick decision time (ms)
TICK_BUDGET_MS = 40

def main():
    print("🧠 Heuristic Agent ready. Waiting for game state...", file=sys.stderr)

    while True:
        line = sys.stdin.readline()
        if not line:
            break  # end of game
        line = line.strip()
        if not line:
            continue

        try:
            state = json.loads(line)
        except json.JSONDecodeError:
            print("⚠️ Invalid JSON received. Skipping.", file=sys.stderr)
            continue

        # Deadline (optional, not used here)
        _ = time.perf_counter() + (TICK_BUDGET_MS / 1000.0)

        # Decide move
        move = choose_move(state)
        print(move)
        sys.stdout.flush()

    print("🏁 Agent terminated.", file=sys.stderr)


if __name__ == "__main__":
    main()

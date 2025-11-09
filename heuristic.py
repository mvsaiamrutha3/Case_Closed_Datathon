#!/usr/bin/env python3
"""
heuristic.py
------------
Heuristic scoring system with optimized DFS + opponent threat estimation.
"""

from board import inb, DELTAS, legal_moves
from copy import deepcopy
from collections import deque

# === Tunable Weights ===
W_CRASH_SELF = -1.0
W_CRASH_OPP = +1.0
W_PATH_DIFF = +0.03
W_HEADON = -0.5
W_RISK = -0.2
W_SURVIVAL = +0.1
W_ENDGAME = +0.3
W_EXPLORATION = +0.05
W_FREEDOM = +0.02
W_TERRITORY_THREAT = -0.02   # 🔥 new: penalize shared zones near opponent
W_FATAL = -9999.0

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------

def simulate_move(board, pos, move):
    dr, dc = DELTAS[move]
    nr, nc = pos[0] + dr, pos[1] + dc
    if not inb(nr, nc) or board[nr][nc] == "X":
        return pos, True
    return (nr, nc), False


def next_legal_moves(board, pos):
    return len(legal_moves(board, pos))


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# === OPTIMIZED LONGEST PATH ===
def longest_safe_path(board, start):
    H, W = len(board), len(board[0])
    memo = {}
    stack = [(start, frozenset())]
    max_len = 0

    while stack:
        pos, visited = stack.pop()
        if pos in memo:
            max_len = max(max_len, memo[pos] + len(visited))
            continue

        best_here = 0
        r, c = pos
        for dr, dc in DELTAS.values():
            nr, nc = r + dr, c + dc
            if not inb(nr, nc):
                continue
            nxt = (nr, nc)
            if board[nr][nc] == "X" or nxt in visited:
                continue
            stack.append((nxt, visited | {pos}))
            best_here = max(best_here, 1)

        memo[pos] = best_here
        max_len = max(max_len, len(visited) + best_here)

    return max_len


# === NEW: Territory Threat Estimation ===
def territorial_threat(board, you, opp, max_depth=6):
    """
    Estimate how much of your reachable area is shared or threatened by opponent.
    Lower is better (less overlap).
    """
    H, W = len(board), len(board[0])
    dist_you = [[None]*W for _ in range(H)]
    dist_opp = [[None]*W for _ in range(H)]

    def bfs(start, dist_map):
        q = deque([(start, 0)])
        dist_map[start[0]][start[1]] = 0
        while q:
            (r, c), d = q.popleft()
            if d >= max_depth:  # limit radius
                continue
            for dr, dc in DELTAS.values():
                nr, nc = r + dr, c + dc
                if not inb(nr, nc): continue
                if board[nr][nc] == "X": continue
                if dist_map[nr][nc] is None:
                    dist_map[nr][nc] = d + 1
                    q.append(((nr, nc), d + 1))

    bfs(you, dist_you)
    bfs(opp, dist_opp)

    threat = 0
    total = 0
    for i in range(H):
        for j in range(W):
            if dist_you[i][j] is not None:
                total += 1
                if dist_opp[i][j] is not None and dist_opp[i][j] <= dist_you[i][j]:
                    threat += 1
    if total == 0:
        return 0.0
    return threat / total  # ratio of cells opponent can reach as fast or faster


# ----------------------------------------------------------------------
# Main heuristic function
# ----------------------------------------------------------------------

def heuristic_score(state, move):
    board = deepcopy(state["board"])
    you = tuple(state["you"])
    opp = tuple(state["opponent"])
    opp_dir = state.get("opponent_last_direction", "UP")

    new_you, crash_you = simulate_move(board, you, move)
    if crash_you:
        return W_FATAL

    board[you[0]][you[1]] = "X"
    board[opp[0]][opp[1]] = "X"

    if not inb(new_you[0], new_you[1]) or board[new_you[0]][new_you[1]] == "X":
        return W_FATAL

    # Path advantage
    my_path_len = longest_safe_path(board, new_you)
    opp_path_len = longest_safe_path(board, opp)
    path_diff = my_path_len - opp_path_len

    # Threat estimation
    threat_ratio = territorial_threat(board, new_you, opp)

    # Risk and positional awareness
    headon = (new_you == opp)
    dr, dc = DELTAS.get(opp_dir, (0, 0))
    predicted = (opp[0] + dr, opp[1] + dc)
    risk = (new_you == predicted)
    endgame = all(cell == "X" for row in board for cell in row)

    # Score aggregation
    score = 0.0
    score += W_SURVIVAL
    score += W_PATH_DIFF * path_diff
    score += W_HEADON * headon
    score += W_RISK * risk
    score += W_TERRITORY_THREAT * threat_ratio  # 🧩 new penalty for shared territory

    if board[new_you[0]][new_you[1]] == " ":
        score += W_EXPLORATION

    freedom = next_legal_moves(board, new_you)
    score += W_FREEDOM * freedom

    if endgame:
        score += W_ENDGAME

    return score

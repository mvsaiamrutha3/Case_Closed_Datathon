# 🤖 Heuristic-Based AI Agent

A Python-based **heuristic AI system** designed for competitive pathfinding and survival games.  
This agent uses logical scoring — not machine learning — to make real-time decisions.

---

## 🧩 Project Files

| File | Description |
|------|--------------|
| **heuristic.py** | Main scoring logic — evaluates possible moves based on survival, space, and threat. |
| **agent.py** | Core AI agent — accepts state input and selects the best move. |
| **search.py** | Contains pathfinding utilities (DFS, BFS). |
| **board.py** | Defines the board grid, helper functions, and move deltas. |

---

## ⚙️ Input Syntax for `agent.py`

The `agent.py` file expects the game **state** as a Python dictionary (or JSON-like structure)  
with the following format:

```python
state = {
    "you": [row, col],               # Your current position
    "opponent": [row, col],          # Opponent's current position
    "board": [                       # 2D grid representing the board
        [" ", " ", "X", " "],
        [" ", "X", " ", " "],
        [" ", " ", " ", " "],
        ["X", " ", " ", "X"]
    ],
    "opponent_last_direction": "UP"  # (optional) last known move of the opponent
}

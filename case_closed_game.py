#!/usr/bin/env python3
"""
case_closed_game.py
-------------------
Standalone simulation for Case Closed.

- Implements the game logic (GameBoard, Agent, Game, etc.)
- Converts internal state into the JSON format expected by agent.py
- Runs agent.py as a subprocess, sends state, reads chosen move
"""

import json
import random
import subprocess
import sys
import time
from collections import deque
from enum import Enum
from typing import Optional

# === CONSTANTS ===
EMPTY = 0
AGENT = 1

# === GAME BOARD ===
class GameBoard:
    def __init__(self, height: int = 18, width: int = 20):
        self.height = height
        self.width = width
        self.grid = [[EMPTY for _ in range(width)] for _ in range(height)]

    def _torus_check(self, position: tuple[int, int]) -> tuple[int, int]:
        x, y = position
        return (x % self.width, y % self.height)
    
    def get_cell_state(self, position: tuple[int, int]) -> int:
        x, y = self._torus_check(position)
        return self.grid[y][x]

    def set_cell_state(self, position: tuple[int, int], state: int):
        x, y = self._torus_check(position)
        self.grid[y][x] = state

    def __str__(self) -> str:
        chars = {EMPTY: '.', AGENT: 'A'}
        return "\n".join(" ".join(chars.get(self.grid[y][x], '?') for x in range(self.width))
                         for y in range(self.height))

# === DIRECTIONS ===
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    RIGHT = (1, 0)
    LEFT = (-1, 0)

class GameResult(Enum):
    AGENT1_WIN = 1
    AGENT2_WIN = 2
    DRAW = 3

# === AGENT ===
class Agent:
    def __init__(self, agent_id: str, start_pos: tuple[int, int], start_dir: Direction, board: GameBoard):
        self.agent_id = agent_id
        second = (start_pos[0] + start_dir.value[0], start_pos[1] + start_dir.value[1])
        self.trail = deque([start_pos, second])
        self.direction = start_dir
        self.board = board
        self.alive = True
        self.length = 2
        self.boosts_remaining = 3
        self.board.set_cell_state(start_pos, AGENT)
        self.board.set_cell_state(second, AGENT)
    
    def is_head(self, position: tuple[int, int]) -> bool:
        return position == self.trail[-1]
    
    def move(self, direction: Direction, other_agent: Optional['Agent'] = None, use_boost: bool = False) -> bool:
        if not self.alive:
            return False
        if use_boost and self.boosts_remaining <= 0:
            use_boost = False
        num_moves = 2 if use_boost else 1
        if use_boost:
            self.boosts_remaining -= 1
        
        for _ in range(num_moves):
            cur_dx, cur_dy = self.direction.value
            req_dx, req_dy = direction.value
            if (req_dx, req_dy) == (-cur_dx, -cur_dy):
                continue
            head = self.trail[-1]
            dx, dy = direction.value
            new_head = (head[0] + dx, head[1] + dy)
            new_head = self.board._torus_check(new_head)
            cell_state = self.board.get_cell_state(new_head)
            self.direction = direction
            if cell_state == AGENT:
                if new_head in self.trail:
                    self.alive = False
                    return False
                if other_agent and other_agent.alive and new_head in other_agent.trail:
                    if other_agent.is_head(new_head):
                        self.alive = False
                        other_agent.alive = False
                        return False
                    else:
                        self.alive = False
                        return False
            self.trail.append(new_head)
            self.length += 1
            self.board.set_cell_state(new_head, AGENT)
        return True

# === GAME ===
class Game:
    def __init__(self):
        self.board = GameBoard()
        self.agent1 = Agent(agent_id=1, start_pos=(1, 2), start_dir=Direction.RIGHT, board=self.board)
        self.agent2 = Agent(agent_id=2, start_pos=(17, 15), start_dir=Direction.LEFT, board=self.board)
        self.turns = 0
    
    def step(self, dir1: Direction, dir2: Direction, boost1: bool = False, boost2: bool = False):
        if self.turns >= 200:
            if self.agent1.length > self.agent2.length:
                return GameResult.AGENT1_WIN
            elif self.agent2.length > self.agent1.length:
                return GameResult.AGENT2_WIN
            else:
                return GameResult.DRAW
        agent_one_alive = self.agent1.move(dir1, other_agent=self.agent2, use_boost=boost1)
        agent_two_alive = self.agent2.move(dir2, other_agent=self.agent1, use_boost=boost2)
        self.turns += 1
        if not agent_one_alive and not agent_two_alive:
            return GameResult.DRAW
        elif not agent_one_alive:
            return GameResult.AGENT2_WIN
        elif not agent_two_alive:
            return GameResult.AGENT1_WIN
        return None

# === BRIDGE TO AGENT.PY ===
MOVE_MAP = {
    "UP": Direction.UP,
    "DOWN": Direction.DOWN,
    "LEFT": Direction.LEFT,
    "RIGHT": Direction.RIGHT,
}

def build_state(game: Game) -> dict:
    """Convert internal game state to JSON format expected by agent.py"""
    board_matrix = []
    for y in range(game.board.height):
        row = []
        for x in range(game.board.width):
            val = game.board.grid[y][x]
            row.append("." if val == 0 else "X")
        board_matrix.append(row)
    you_pos = game.agent1.trail[-1]
    return {
        "board": board_matrix,
        "you": [you_pos[1], you_pos[0]],  # [row, col]
        "turn": game.turns,
    }

# === MAIN LOOP ===
def main():
    print("🎮 Starting Case Closed Simulation")
    game = Game()

    # Launch agent.py as subprocess
    agent_proc = subprocess.Popen(
        [sys.executable, "agent.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    result = None
    while True:
        state_json = json.dumps(build_state(game))
        agent_proc.stdin.write(state_json + "\n")
        agent_proc.stdin.flush()

        move = agent_proc.stdout.readline().strip()
        if move not in MOVE_MAP:
            print(f"⚠️ Invalid move from agent: {move}. Using RIGHT.")
            move_dir = Direction.RIGHT
        else:
            move_dir = MOVE_MAP[move]

        # Opponent fixed for now
        result = game.step(move_dir, Direction.LEFT)

        print(f"\nTurn {game.turns}")
        print(game.board)

        if result:
            print(f"🏁 Game Over: {result.name}")
            break

        time.sleep(0.05)

    agent_proc.stdin.close()
    agent_proc.terminate()
    agent_proc.wait(timeout=1)

if __name__ == "__main__":
    main()

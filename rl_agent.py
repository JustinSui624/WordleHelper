import random
import json
from typing import Dict
from collections import Counter
from config import ALPHA, GAMMA, EPSILON

class RLAgent:
    def __init__(self):
        self.q_table: Dict[str, float] = {}
        try:
            with open('q_table.json', 'r') as f:
                self.q_table = json.load(f)
        except FileNotFoundError:
            pass

    def _state_key(self, possible_count: int, turn: int) -> str:
        bucket = min(possible_count // 50, 20)
        return f"{bucket}_{turn}"

    def choose_action(self, candidates: set, turn: int) -> str:
        state = self._state_key(len(candidates), turn)
        if random.random() < EPSILON:
            return random.choice(list(candidates))
        q_vals = {w: self.q_table.get(f"{state}_{w}", 0) for w in candidates}
        if not q_vals:
             return random.choice(list(candidates)) # Fallback if no Q-values found
        return max(q_vals, key=q_vals.get)

    def update(self, state: str, action: str, reward: float, next_state: str):
        old = self.q_table.get(f"{state}_{action}", 0)
        # Simplified future action space for approximation
        future = max(self.q_table.get(f"{next_state}_{w}", 0) for w in ['A', 'B', 'C', 'D', 'E', action])
        self.q_table[f"{state}_{action}"] = old + ALPHA * (reward + GAMMA * future - old)

    def save(self, path="q_table.json"):
        with open(path, 'w') as f:
            json.dump(self.q_table, f)
# knowledge.py
from typing import List, Set, Tuple
from collections import Counter
from config import ANSWERS, GUESSABLE, WORD_LIST_PATH, GUESSABLE_PATH
from pathlib import Path


class WordleKnowledge:
    def __init__(self):
        try:
            self.answers = [line.strip().upper() for line in WORD_LIST_PATH.open() if line.strip()]
            self.guessable = [line.strip().upper() for line in GUESSABLE_PATH.open() if line.strip()]
        except FileNotFoundError:
            self.answers = [w.upper() for w in ANSWERS]
            self.guessable = [w.upper() for w in GUESSABLE]

        self.possible = set(self.answers)
        self.constraints: List[Tuple[str, str]] = []

    def apply_feedback(self, guess: str, feedback: str):
        self.constraints.append((guess, feedback))
        new_possible = {w for w in self.possible if self._matches_feedback(w, guess, feedback)}
        self.possible = new_possible

    def _matches_feedback(self, word: str, guess: str, feedback: str) -> bool:
        from search import feedback_pattern  # Localized import
        return feedback_pattern(guess, word) == feedback

    def reset(self):
        self.possible = set(self.answers)
        self.constraints = []
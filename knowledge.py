from typing import List, Set, Tuple
from collections import Counter  # Added: For letter counting
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
        w_count = Counter(word)  # Now defined
        g_count = Counter(guess)

        # Track used yellows to handle multiples
        used_yellows = Counter()

        for i, (w_char, g_char, f) in enumerate(zip(word, guess, feedback)):
            if f == 'G':
                if w_char != g_char:
                    return False
                w_count[w_char] -= 1
                g_count[g_char] -= 1
            elif f == 'Y':
                if w_char == g_char or g_count[g_char] == 0 or w_count.get(g_char, 0) == 0:
                    return False
                # Check if this yellow is already "used" for multiples
                if used_yellows[g_char] >= w_count[g_char]:
                    return False
                used_yellows[g_char] += 1
            elif f == 'B':
                if w_char == g_char:
                    return False
                # For grays, ensure the letter isn't required elsewhere
                if g_char in word and g_count[g_char] > sum(1 for j, fc in enumerate(feedback) if fc != 'B' and guess[j] == g_char):
                    return False

        # Final check: All greens/yellows accounted for
        for char in g_count:
            if g_count[char] > w_count.get(char, 0) + used_yellows.get(char, 0):
                return False
        return True

    def reset(self):
        self.possible = set(self.answers)
        self.constraints = []
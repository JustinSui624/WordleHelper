from typing import Set
from collections import Counter
import math

def feedback_pattern(guess: str, answer: str) -> str:
    result = ['B'] * 5
    a_count = Counter(answer)
    # Greens
    for i in range(5):
        if guess[i] == answer[i]:
            result[i] = 'G'
            a_count[guess[i]] -= 1
    # Yellows
    for i in range(5):
        if result[i] != 'G' and guess[i] in a_count and a_count[guess[i]] > 0:
            result[i] = 'Y'
            a_count[guess[i]] -= 1
    return ''.join(result)

def entropy(word: str, candidates: Set[str]) -> float:
    patterns = Counter(feedback_pattern(word, c) for c in candidates)
    total = len(candidates)
    if total == 0:
        return 0.0
    return -sum((count / total * math.log2(count / total) for count in patterns.values() if count > 0))

def best_guess(candidates: Set[str], guessable: list) -> str:
    if len(candidates) <= 2:
        return list(candidates)[0]
    return max(guessable, key=lambda w: entropy(w, candidates))
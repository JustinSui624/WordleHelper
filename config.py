from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
WORD_LIST_PATH = DATA_DIR / "wordle_answers.txt"
GUESSABLE_PATH = DATA_DIR / "wordle_guessable.txt"

ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.08
MAX_GUESSES = 6

# Demo hardcoded (expand with files)
ANSWERS = ["crane", "slate", "trace", "raise", "stare", "jazz", "flood", "aback", "abase"]
GUESSABLE = ANSWERS + ["audio", "about", "alert", "being", "below", "abide", "acrid"]
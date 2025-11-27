# config.py

from pathlib import Path

# --- WORD LISTS ---
WORD_LIST_PATH = Path("wordle_answers.txt")
GUESSABLE_PATH = Path("word_list.txt")

# Default/Fallback words (used if file loading fails)
# These must be the same size for the code to run initially
ANSWERS = ["SLATE", "CRANE", "TRACE", "RAISE", "STARE", "ABACK", "ABATE", "APPLE", "BRAVE", "CLIMB", "SOLVE", "TRAIN", "HOUSE", "EARTH", "DREAM"]
GUESSABLE = ANSWERS

# --- GAME SETTINGS ---
MAX_GUESSES = 6

# --- RL AGENT SETTINGS ---
ALPHA = 0.1    # Learning rate
GAMMA = 0.9    # Discount factor
EPSILON = 0.3  # Exploration rate (30% chance to use RL)
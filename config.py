# config.py

from pathlib import Path

from pathlib import Path

# Define the BASE_DIR as the directory where config.py lives
BASE_DIR = Path(__file__).resolve().parent

# --- WORD LISTS ---
# Use BASE_DIR to ensure the files are found relative to this file
WORD_LIST_PATH = BASE_DIR / "wordle_answers.txt"
GUESSABLE_PATH = BASE_DIR / "word_list.txt"

ANSWERS = ["CIGAR", "REBUS", "SASSY", "HUMPH", "AWAKE", "BLUSH", "FOCAL", "EVADE", "NAVAL", "SERVE", "HEATH", "DWARF", "MODEL", "KARMA", "STINK", "GRADE", "QUIET", "BENCH", "ABATE", "FEIGN", "SLATE", "CRANE", "TRACE", "RAISE", "STARE"]
GUESSABLE = ANSWERS  # or load from full list

MAX_GUESSES = 6
ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.3
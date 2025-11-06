#!/usr/bin/env python3
import sys
import os

# Add src/ to Python path (fix for running from project root)
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from solver import WordleSolver
from utils import print_game_state

def main():
    s = WordleSolver()
    s.start_game()
    while not s.game_over:
        guess = s.get_guess()
        print(f"Guess: {guess}")
        if "ERROR" in guess:
            print("Invalid feedback filtered all words. Try again.")
            continue
        print_game_state(s)
        while True:
            fb = input("Feedback (G/Y/B only, 5 chars): ").strip()
            try:
                s.submit_feedback(fb)
                break
            except ValueError as e:
                print(f"Error: {e}")
    print(f"Solved in {s.turn} guesses!")

if __name__ == "__main__":
    main()
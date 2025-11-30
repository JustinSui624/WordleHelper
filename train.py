# train.py
# FINAL VERSION — SHOWS REAL-TIME PROGRESS

import random
import time
from statistics import mean
from solver import WordleSolver
from config import MAX_GUESSES

def train_rl(episodes: int = 10000, output_file: str = "q_table.json"):
    solver = WordleSolver()
    wins = []
    guesses_list = []

    print(f"Starting training for {episodes} episodes...")
    start_time = time.time()

    for ep in range(1, episodes + 1):
        # Force Engine Mode with a real secret word
        secret = random.choice(solver.kb.answers)
        solver.start_game(answer=secret)

        guesses = 0
        solved = False

        while not solver.game_over and guesses < MAX_GUESSES:
            guess = solver.get_guess()
            solver.last_guess = guess

            result = solver.submit_feedback("")  # Auto-feedback in Engine Mode
            guesses += 1

            if result["solved"]:
                solved = True
                break

        wins.append(1 if solved else 0)
        guesses_list.append(guesses if solved else MAX_GUESSES)

        # SHOW PROGRESS EVERY 100 EPISODES
        if ep % 100 == 0:
            recent_win_rate = mean(wins[-100:]) * 100
            recent_avg_guesses = mean(guesses_list[-100:])
            elapsed = time.time() - start_time
            print(f"Ep {ep:5d} | Win Rate: {recent_win_rate:5.1f}% | "
                  f"Avg Guesses: {recent_avg_guesses:.2f} | "
                  f"Time: {elapsed/60:.1f} min")

    # Final save
    solver.rl.save(output_file)

    total_time = (time.time() - start_time) / 60
    overall_win_rate = mean(wins) * 100
    print(f"\nTRAINING COMPLETE!")
    print(f"Final Win Rate: {overall_win_rate:.2f}%")
    print(f"Average Guesses: {mean(guesses_list):.2f}")
    print(f"Total Time: {total_time:.1f} minutes")
    print(f"Q-table saved → {output_file}")

if __name__ == "__main__":
    train_rl(episodes=10000)
#!/usr/bin/env python3
"""
train.py - RL Training Script for Wordle AI Solver

Run: python train.py --episodes 10000 --output q_table.json
Trains the Q-Learning agent on simulated games, logging win rates and avg. guesses.
"""

import argparse
import time
from statistics import mean

# CRITICAL IMPORTS: Ensure these files exist in your project directory
from solver import WordleSolver
# Assuming config.py contains constants like MAX_GUESSES
# If config.py is missing, MAX_GUESSES will need to be defined here (e.g., MAX_GUESSES = 6)
from config import MAX_GUESSES


def train_rl(episodes: int, output_file: str = "q_table.json"):
    """
    Runs the autonomous RL training loop for a specified number of episodes.
    """
    solver = WordleSolver()
    wins = []
    guesses_per_game = []
    start_time = time.time()

    print(f"Starting RL Training: {episodes} episodes...")
    for episode in range(episodes):
        # Start a new game. We pass None to ensure the solver chooses a random answer
        # (Engine Mode is active with a secret word)
        solver.start_game(answer=None)

        game_guesses = 0
        game_won = False

        while not solver.game_over and game_guesses < MAX_GUESSES:
            # 1. Get the AI's guess (from RL or Planner)
            guess = solver.get_guess()

            # 💡 CRITICAL FIX: Manually set the solver's last_guess variable.
            # This is essential because submit_feedback() now requires the guess
            # to be pre-stored before it is called.
            solver.last_guess = guess

            if "ERROR" in guess:
                print(f"Warning: Episode {episode + 1} hit an ERROR state with 0 possible words.")
                break

            # 2. Submit feedback. Pass "" to signal Engine Mode (auto-feedback).
            feedback = solver.submit_feedback("")
            game_guesses += 1

            if feedback['solved']:
                game_won = True
                break

        # Record results for logging
        wins.append(1 if game_won else 0)
        guesses_per_game.append(game_guesses)

        # Log progress every 100 episodes
        if (episode + 1) % 100 == 0:
            win_rate = mean(wins[-100:]) * 100
            avg_guesses = mean(guesses_per_game[-100:])
            elapsed = time.time() - start_time
            print(
                f"Ep {episode + 1}: Win Rate: {win_rate:.1f}% | Avg Guesses: {avg_guesses:.2f} | Time: {elapsed / 60:.1f}m")

    # Final save of the learned Q-table
    solver.rl.save(output_file)
    overall_win_rate = mean(wins) * 100
    overall_avg_guesses = mean(guesses_per_game)
    total_time = time.time() - start_time

    print(f"\n=== TRAINING COMPLETE ===")
    print(f"Episodes: {episodes} | Win Rate: {overall_win_rate:.1f}% | Avg Guesses: {overall_avg_guesses:.2f}")
    print(f"Total Time: {total_time / 60:.1f} min | Speed: {episodes / (total_time / 60):.0f} eps/min")
    print(f"Q-Table saved to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Wordle RL Agent")
    parser.add_argument("--episodes", type=int, default=10000, help="Number of training episodes")
    parser.add_argument("--output", type=str, default="q_table.json", help="Output Q-table file")
    args = parser.parse_args()
    train_rl(args.episodes, args.output)
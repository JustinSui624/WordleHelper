# solver.py (Updated for Dual Mode)

import random
from knowledge import WordleKnowledge
from planning import Planner
from rl_agent import RLAgent
from nlp_feedback import parse_feedback
from search import feedback_pattern
from config import MAX_GUESSES


class WordleSolver:
    def __init__(self):
        self.kb = WordleKnowledge()
        self.planner = Planner(self.kb)
        self.rl = RLAgent()
        self.turn = 0
        self.game_over = False
        self.answer = None
        self.last_guess = ""

    def start_game(self, answer: str = None):
        self.kb.reset()
        self.turn = 0
        self.game_over = False
        self.last_guess = ""

        if answer is None or answer == "HELPER_MODE":
            self.answer = None  # Helper Mode
        else:
            self.answer = answer.upper()  # Engine Mode — THIS MUST BE SET

    def get_guess(self) -> str:
        if self.turn == 0:
            return "SLATE"
        elif len(self.kb.possible) == 0:
            return "ERROR: No possible words left—Check feedback!"
        elif len(self.kb.possible) <= 2:
            return random.choice(list(self.kb.possible))
        else:
            if random.random() < 0.3:
                return self.rl.choose_action(self.kb.possible, self.turn)
            return self.planner.plan_next_guess()

    def submit_feedback(self, feedback_text: str):
        guess = self.last_guess
        if not guess:
            raise ValueError("Solver error: No guess was made.")

        actual = ""
        if self.answer:
            # 🤖 Engine Mode: Answer is set, calculate feedback
            actual = feedback_pattern(guess, self.answer)
        elif feedback_text:
            # ✍️ Helper Mode: Answer is None, use and parse user's text feedback
            actual = parse_feedback(feedback_text)
        else:
            # Should be caught by the UI, but here for robustness
            raise ValueError("Feedback required. Please enter 5 G/Y/B characters.")

        if len(self.kb.possible) == 0 and actual != "GGGGG":
            raise ValueError(f"Feedback '{actual}' is inconsistent with history. No possible words left.")

        self.kb.apply_feedback(guess, actual)

        # --- RL Update Logic (Used in both modes) ---
        state = self.rl._state_key(len(self.kb.possible), self.turn)
        next_state = self.rl._state_key(len(self.kb.possible), self.turn + 1)
        reward = 10 if actual == "GGGGG" else -1 * (self.turn + 1)
        self.rl.update(state, guess, reward, next_state)
        # --- End RL Update Logic ---

        self.turn += 1

        if actual == "GGGGG" or self.turn >= MAX_GUESSES:
            self.game_over = True
            self.rl.save()

        return {
            "guess": guess,
            "feedback": actual,
            "remaining": len(self.kb.possible),
            "solved": actual == "GGGGG"
        }
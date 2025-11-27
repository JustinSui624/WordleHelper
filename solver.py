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
        self.last_guess = ""  # 🟢 FIXED: Variable to track the guess made

    def start_game(self, answer: str = None):
        self.kb.reset()
        self.turn = 0
        self.game_over = False
        self.last_guess = ""  # Reset last guess

        # Determine Mode:
        if answer is None:
            # If no answer is provided (as in train.py), activate Engine Mode with a random word.
            self.answer = random.choice(self.kb.answers).upper()
        elif answer.upper() == "HELPER_MODE":
            # If the GUI passes a specific flag, activate Helper Mode.
            self.answer = None
        else:
            # If a specific word is provided (Demo), use it.
            self.answer = answer.upper()

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
        # 🟢 FIXED: Use the guess pre-set by the GUI/Training script
        guess = self.last_guess

        if not guess:
            raise ValueError("Solver error: No guess was made. Set self.last_guess first.")

        actual = ""

        # 🟢 FIXED: Corrected mode check logic
        if self.answer:
            # 🤖 Engine Mode (self.answer is set): Calculate feedback automatically
            actual = feedback_pattern(guess, self.answer)
        elif feedback_text:
            # ✍️ Helper Mode (self.answer is None): Use user's input
            actual = parse_feedback(feedback_text)
        else:
            # This block is now ONLY reached if Helper Mode is active AND no feedback was entered.
            raise ValueError("Feedback required. Please enter 5 G/Y/B characters for Helper Mode.")

        self.kb.apply_feedback(guess, actual)

        # --- RL Update Logic ---
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
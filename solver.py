import random
from knowledge import WordleKnowledge  # Absolute (no .)
from planning import Planner
from rl_agent import RLAgent
from nlp_feedback import parse_feedback
from search import feedback_pattern
from config import MAX_GUESSES  # Assuming c
import random
from knowledge import WordleKnowledge  # Absolute (no .)
from planning import Planner
from rl_agent import RLAgent
from nlp_feedback import parse_feedback
from search import feedback_pattern
from config import MAX_GUESSES  # Assuming config is in src/
class WordleSolver:
    def __init__(self):
        self.kb = WordleKnowledge()
        self.planner = Planner(self.kb)
        self.rl = RLAgent()
        self.turn = 0
        self.game_over = False
        self.answer = None

    def start_game(self, answer: str = None):
        self.kb.reset()
        self.turn = 0
        self.game_over = False
        self.answer = answer.upper() if answer else random.choice(self.kb.answers).upper()

    def get_guess(self) -> str:
        if self.turn == 0:
            return "SLATE"
        elif len(self.kb.possible) == 0:
            return "ERROR: No possible words left—Check feedback!"  # Graceful fallback
        elif len(self.kb.possible) <= 2:
            return list(self.kb.possible)[0]
        else:
            if random.random() < 0.3:
                return self.rl.choose_action(self.kb.possible, self.turn)
            return self.planner.plan_next_guess()

    def submit_feedback(self, feedback_text: str):
        guess = self.get_guess()
        parsed = parse_feedback(feedback_text)
        actual = parsed
        if self.answer:
            actual = feedback_pattern(guess, self.answer)
        self.kb.apply_feedback(guess, actual)
        state = self.rl._state_key(len(self.kb.possible), self.turn)
        next_state = self.rl._state_key(len(self.kb.possible), self.turn + 1)
        reward = 10 if actual == "GGGGG" else -1 * (self.turn + 1)
        self.rl.update(state, guess, reward, next_state)
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
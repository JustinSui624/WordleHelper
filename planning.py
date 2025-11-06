from search import best_guess

class Planner:
    def __init__(self, knowledge):
        self.kb = knowledge

    def plan_next_guess(self) -> str:
        return best_guess(self.kb.possible, self.kb.guessable)
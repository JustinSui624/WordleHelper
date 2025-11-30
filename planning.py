# planning.py
class Planner:
    def __init__(self, knowledge):
        self.kb = knowledge

    def plan_next_guess(self) -> str:
        from search import best_guess  # Localized!

        if not self.kb or not self.kb.possible:
            return "SLATE"

        return best_guess(self.kb.possible, self.kb.guessable)
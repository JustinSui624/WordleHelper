import random
from typing import List, Tuple

class WordleGame:
    def __init__(self, word_list: List[str] = None):
        """
        Initialize the Wordle game with a list of possible words.
        If no list provided, uses a default set of common 5-letter words.
        """
        if word_list is None:
            self.word_list = [
                "APPLE", "BRAVE", "CLIMB", "DREAM", "EARTH", "FLAME", "GRAPE", "HOUSE",
                "IGLOO", "JUICE", "KNIGHT", "LIGHT", "MAGIC", "NIGHT", "OCEAN", "PEACE",
                "QUEEN", "RIVER", "SMILE", "TIGER", "UMBRA", "VOICE", "WATER", "YOUTH",
                "ZEBRA", "ALBUM", "BEACH", "CHESS", "DANCE", "EAGLE", "FROST", "GHOST",
                "HONEY", "IVORY", "JOKER", "LEMON", "MUSIC", "NINJA", "OLIVE", "PIANO",
                "ROBOT", "SHARK", "TULIP", "URBAN", "VIXEN", "WHALE", "XENON", "YACHT",
                "ABYSS", "BLITZ", "CYCLE", "DWARF", "EMBED", "FJORD", "GYPSY", "HAZEL"
            ]
        else:
            self.word_list = [word.upper() for word in word_list if len(word) == 5]
        
        if not self.word_list:
            raise ValueError("No valid 5-letter words provided")
        
        self.secret_word = random.choice(self.word_list)
        self.attempts = []
        self.feedback_history = []
        self.max_attempts = 6
        self.game_over = False
        self.won = False

    def get_feedback(self, guess: str) -> List[Tuple[str, str]]:
        """
        Compare guess with secret word and return feedback.
        Returns: List of tuples (letter, color) where color is 'green', 'yellow', or 'gray'
        """
        guess = guess.upper()
        feedback = []
        secret_list = list(self.secret_word)
        guess_list = list(guess)
        
        # First pass: mark correct positions (green)
        for i in range(len(guess_list)):
            if guess_list[i] == secret_list[i]:
                feedback.append((guess_list[i], 'green'))
                secret_list[i] = None  # Mark as used
                guess_list[i] = None   # Mark as processed
            else:
                feedback.append((guess_list[i], 'gray'))  # Temporary, will update for yellows
        
        # Second pass: mark correct letters in wrong position (yellow)
        for i in range(len(guess_list)):
            if guess_list[i] is not None and guess_list[i] in secret_list:
                feedback[i] = (guess_list[i], 'yellow')
                # Remove the first occurrence from secret list
                secret_list[secret_list.index(guess_list[i])] = None
        
        return feedback

    def make_guess(self, guess: str) -> Tuple[bool, List[Tuple[str, str]]]:
        """
        Make a guess and return (success, feedback)
        success: True if guess is valid, False otherwise
        """
        guess = guess.upper().strip()
        
        # Validate guess
        if self.game_over:
            return False, "Game is over!"
        
        if len(guess) != 5:
            return False, "Guess must be 5 letters!"
        
        if guess not in self.word_list:
            return False, "Word not in word list!"
        
        if guess in self.attempts:
            return False, "You already tried that word!"
        
        # Process valid guess
        self.attempts.append(guess)
        feedback = self.get_feedback(guess)
        self.feedback_history.append(feedback)
        
        # Check game status
        if guess == self.secret_word:
            self.game_over = True
            self.won = True
        elif len(self.attempts) >= self.max_attempts:
            self.game_over = True
        
        return True, feedback

    def display_board(self):
        """Display the current game board with colored feedback"""
        print(f"\nWORDLE - Attempts: {len(self.attempts)}/{self.max_attempts}")
        print("=" * 30)
        
        for i in range(self.max_attempts):
            if i < len(self.attempts):
                guess = self.attempts[i]
                feedback = self.feedback_history[i]
                
                display_line = ""
                for letter, color in feedback:
                    if color == 'green':
                        display_line += f" [{letter}] "
                    elif color == 'yellow':
                        display_line += f" ({letter}) "
                    else:
                        display_line += f"  {letter}  "
                print(display_line)
            else:
                print("  _     _     _     _     _  ")
        
        print("=" * 30)
        
        if self.game_over:
            if self.won:
                print(f"🎉 Congratulations! You won in {len(self.attempts)} attempts!")
            else:
                print(f"💀 Game over! The word was: {self.secret_word}")

    def get_colored_feedback(self, feedback: List[Tuple[str, str]]) -> str:
        """
        Return a colored string representation of feedback using ANSI colors
        """
        colored_str = ""
        for letter, color in feedback:
            if color == 'green':
                colored_str += f"\033[92m{letter}\033[0m"  # Green
            elif color == 'yellow':
                colored_str += f"\033[93m{letter}\033[0m"  # Yellow
            else:
                colored_str += f"\033[90m{letter}\033[0m"  # Gray
        return colored_str

def load_words_from_file(filename: str) -> List[str]:
    """Load words from a text file (one word per line)"""
    try:
        with open(filename, 'r') as file:
            words = [line.strip().upper() for line in file if len(line.strip()) == 5]
        return words
    except FileNotFoundError:
        print(f"Warning: File {filename} not found. Using default word list.")
        return None

def main():
    """Main game loop"""
    print("Welcome to Wordle!")
    print("Guess the 5-letter word in 6 attempts or less!")
    print("Feedback: [G]reen = correct letter & position, (Y)ellow = correct letter wrong position, Gray = letter not in word")
    
    # Try to load words from file, or use default
    word_list = load_words_from_file("word_list.txt")
    game = WordleGame(word_list)
    
    while not game.game_over:
        game.display_board()
        
        guess = input("\nEnter your guess: ").strip().upper()
        
        success, result = game.make_guess(guess)
        
        if not success:
            print(f"❌ {result}")
        else:
            print(f"Feedback: {game.get_colored_feedback(result)}")
    
    # Final display
    game.display_board()
    
    # Play again?
    play_again = input("\nWould you like to play again? (y/n): ").lower().strip()
    if play_again == 'y':
        main()
    else:
        print("Thanks for playing!")

if __name__ == "__main__":
    main()



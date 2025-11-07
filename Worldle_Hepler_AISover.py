import random
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import List, Set, Tuple, Dict
from collections import Counter
import sys
import os
from datetime import datetime

# Add src/ to Python path if running from project root (for AI modules)
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import AI components (from  AI part)
from solver import WordleSolver
from knowledge import WordleKnowledge


# Wordle Game Engine (from wordle_copy.py)
class WordleGame:
    def __init__(self, word_list: List[str] = None):
        """
        Initialize the Wordle game with a list of possible answers.
        If no list provided, uses a default set of common 5-letter words.
        """
        if word_list is None:
            self.word_list = [
                "CRANE", "SLATE", "TRACE", "RAISE", "STARE", "ABACK", "ABASE", "ABATE", "ABBED", "ABBES"
                # Add more from your wordle_answers.txt or extend as needed
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
                guess_list[i] = None  # Mark as processed
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


# Wordle Helper & AI Integration (combined from WordleHelper.py +  AI part)
class WordleHelper:
    def __init__(self, word_list_path: str = "wordle_answers.txt"):
        self.all_words = self.load_words_from_file(word_list_path)
        if not self.all_words:
            self.all_words = self.get_default_word_list()

        self.possible_words = self.all_words.copy()
        self.green_letters = [""] * 5
        self.yellow_letters = []
        self.gray_letters = set()
        self.yellow_rows = 1

        # Integrate AI solver
        self.ai_solver = WordleSolver()
        self.ai_solver.kb.answers = self.all_words  # Use your word list
        self.ai_solver.kb.guessable = self.all_words  # Simplified for helper

        # Game instance
        self.game = WordleGame(self.all_words)

        self.setup_gui()
        self.update_possible_words()

    def load_words_from_file(self, filepath: str) -> List[str]:
        """Load words from text file"""
        try:
            with open(filepath, 'r') as f:
                words = [line.strip().upper() for line in f if len(line.strip()) == 5]
            return words
        except FileNotFoundError:
            print(f"Warning: {filepath} not found. Using default word list.")
            return []

    def get_default_word_list(self) -> List[str]:
        """Fallback word list"""
        return ["APPLE", "BRAVE", "CLIMB", "DREAM", "EARTH", "FLAME", "GRAPE", "HOUSE", "CRANE", "SLATE"]

    def setup_gui(self):
        """Create the main interface"""
        self.root = tk.Tk()
        self.root.title("Wordle Helper with AI Solver")
        self.root.geometry("900x800")

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        title_label = ttk.Label(main_frame, text="Wordle Helper with AI Solver", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Game board section
        game_frame = ttk.LabelFrame(main_frame, text="Game Board", padding="10")
        game_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.game_display = scrolledtext.ScrolledText(game_frame, height=6, font=("Consolas", 10))
        self.game_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Button to make AI guess
        ai_guess_btn = ttk.Button(game_frame, text="AI Make Guess", command=self.make_ai_guess)
        ai_guess_btn.grid(row=1, column=0, pady=5)

        game_frame.columnconfigure(0, weight=1)
        game_frame.rowconfigure(0, weight=1)

        # Green letters
        green_frame = ttk.LabelFrame(main_frame, text="🟩 Green Letters (Correct Position)", padding="10")
        green_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.setup_green_section(green_frame)

        # Yellow letters
        yellow_frame = ttk.LabelFrame(main_frame, text="🟨 Yellow Letters (Wrong Position)", padding="10")
        yellow_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.setup_yellow_section(yellow_frame)

        # Gray letters
        gray_frame = ttk.LabelFrame(main_frame, text="⬜ Gray Letters (Not in Word)", padding="10")
        gray_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.setup_gray_section(gray_frame)

        # Controls
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(control_frame, text="Update Results", command=self.update_possible_words).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Add Yellow Row", command=self.add_yellow_row).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="New Game", command=self.new_game).pack(side=tk.LEFT, padx=5)

        # Results
        results_frame = ttk.LabelFrame(main_frame, text="Possible Words & AI Suggestion", padding="10")
        results_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)

        self.setup_results_section(results_frame)

    def setup_green_section(self, parent):
        green_subframe = ttk.Frame(parent)
        green_subframe.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.green_entries = []
        for i in range(5):
            label = ttk.Label(green_subframe, text=f"Pos {i + 1}:")
            label.grid(row=0, column=i * 2, padx=(10, 5), pady=5)

            entry = ttk.Entry(green_subframe, width=3, font=("Arial", 14), justify='center')
            entry.grid(row=0, column=i * 2 + 1, padx=(0, 10), pady=5)
            entry.bind('<KeyRelease>', lambda e, pos=i: self.on_green_change(pos))
            self.green_entries.append(entry)

    def setup_yellow_section(self, parent):
        self.yellow_frame_container = ttk.Frame(parent)
        self.yellow_frame_container.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.yellow_rows_frame = ttk.Frame(self.yellow_frame_container)
        self.yellow_rows_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.yellow_row_widgets = []

        self.add_yellow_row()

    def add_yellow_row(self):
        row_index = len(self.yellow_row_widgets)
        row_frame = ttk.Frame(self.yellow_rows_frame)
        row_frame.grid(row=row_index, column=0, sticky=(tk.W, tk.E), pady=2)

        letter_label = ttk.Label(row_frame, text="Letter:")
        letter_label.grid(row=0, column=0, padx=(10, 5))

        letter_entry = ttk.Entry(row_frame, width=3, font=("Arial", 12), justify='center')
        letter_entry.grid(row=0, column=1, padx=5)

        pos_label = ttk.Label(row_frame, text="Not in positions:")
        pos_label.grid(row=0, column=2, padx=(20, 5))

        position_vars = []
        position_checks = []
        for i in range(5):
            var = tk.BooleanVar()
            check = ttk.Checkbutton(row_frame, text=str(i + 1), variable=var)
            check.grid(row=0, column=3 + i, padx=2)
            position_vars.append(var)
            position_checks.append(check)

        delete_btn = ttk.Button(row_frame, text="✕", width=3,
                                command=lambda idx=row_index: self.remove_yellow_row(idx))
        delete_btn.grid(row=0, column=8, padx=(10, 5))

        row_widgets = {
            'frame': row_frame,
            'letter_entry': letter_entry,
            'position_vars': position_vars,
            'delete_btn': delete_btn
        }
        self.yellow_row_widgets.append(row_widgets)

        letter_entry.bind('<KeyRelease>', lambda e: self.update_possible_words())
        for var in position_vars:
            var.trace('w', lambda *args: self.update_possible_words())

    def remove_yellow_row(self, row_index):
        if len(self.yellow_row_widgets) <= 1:
            messagebox.showinfo("Info", "You need at least one yellow letter row")
            return

        self.yellow_row_widgets[row_index]['frame'].destroy()
        self.yellow_row_widgets.pop(row_index)

        for i, widgets in enumerate(self.yellow_row_widgets):
            widgets['frame'].grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
            widgets['delete_btn'].config(command=lambda idx=i: self.remove_yellow_row(idx))

        self.update_possible_words()

    def setup_gray_section(self, parent):
        gray_subframe = ttk.Frame(parent)
        gray_subframe.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.gray_entry = ttk.Entry(gray_subframe, width=30, font=("Arial", 12))
        self.gray_entry.grid(row=0, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        self.gray_entry.bind('<KeyRelease>', lambda e: self.on_gray_change())

        gray_help = ttk.Label(gray_subframe, text="Enter all gray letters (no spaces)")
        gray_help.grid(row=1, column=0, sticky=tk.W, padx=10)

    def setup_results_section(self, parent):
        self.count_label = ttk.Label(parent, text="0 possible words", font=("Arial", 12, "bold"))
        self.count_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.results_text = scrolledtext.ScrolledText(parent, width=80, height=15, font=("Consolas", 10))
        self.results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.ai_suggestion_label = ttk.Label(parent, text="AI Suggestion: None", font=("Arial", 12, "bold"))
        self.ai_suggestion_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))

        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

    def on_green_change(self, position):
        entry = self.green_entries[position]
        text = entry.get().upper()

        if len(text) > 1:
            entry.delete(1, tk.END)
            text = text[0]
            entry.insert(0, text)

        if text and not text.isalpha():
            entry.delete(0, tk.END)
            text = ""

        self.green_letters[position] = text
        self.update_possible_words()

    def on_gray_change(self):
        text = self.gray_entry.get().upper()

        filtered_text = ''.join([c for c in text if c.isalpha()])
        if filtered_text != text:
            self.gray_entry.delete(0, tk.END)
            self.gray_entry.insert(0, filtered_text)
            text = filtered_text

        self.gray_letters = set(text)
        self.update_possible_words()

    def update_yellow_letters(self):
        self.yellow_letters = []

        for row_widgets in self.yellow_row_widgets:
            letter = row_widgets['letter_entry'].get().upper()
            if letter and len(letter) == 1 and letter.isalpha():
                positions = []
                for i, var in enumerate(row_widgets['position_vars']):
                    if var.get():
                        positions.append(i)

                if positions:
                    self.yellow_letters.append({
                        'letter': letter,
                        'positions': positions
                    })

    def update_possible_words(self):
        self.update_yellow_letters()

        possible = []

        for word in self.all_words:
            word_upper = word.upper()
            valid = True

            for i, required_letter in enumerate(self.green_letters):
                if required_letter and word_upper[i] != required_letter:
                    valid = False
                    break

            if not valid:
                continue

            for gray_letter in self.gray_letters:
                if gray_letter in word_upper:
                    is_required = False
                    for yellow_info in self.yellow_letters:
                        if yellow_info['letter'] == gray_letter:
                            is_required = True
                            break
                    if gray_letter in self.green_letters:
                        is_required = True

                    if not is_required:
                        valid = False
                        break

            if not valid:
                continue

            for yellow_info in self.yellow_letters:
                letter = yellow_info['letter']
                positions = yellow_info['positions']

                # Letter must be in word
                if letter not in word_upper:
                    valid = False
                    break

                for pos in positions:
                    if word_upper[pos] == letter:
                        valid = False
                        break

            if valid:
                possible.append(word)

        self.possible_words = possible
        self.display_results()

    def display_results(self):
        self.results_text.delete(1.0, tk.END)

        count = len(self.possible_words)
        self.count_label.config(text=f"{count} possible words")

        if count == 0:
            self.results_text.insert(tk.END, "No words match your criteria!\n\n")
            self.results_text.insert(tk.END, "Check your inputs:\n")
            self.results_text.insert(tk.END, "- Green letters must be in exact positions\n")
            self.results_text.insert(tk.END, "- Yellow letters must be in word but not in marked positions\n")
            self.results_text.insert(tk.END, "- Gray letters should not be in word (unless also yellow/green)")
        else:
            words_per_line = 8
            for i, word in enumerate(self.possible_words):
                self.results_text.insert(tk.END, word)
                if (i + 1) % words_per_line == 0:
                    self.results_text.insert(tk.END, '\n')
                else:
                    self.results_text.insert(tk.END, ' ')

            # AI Suggestion
            if count > 0:
                self.ai_solver.kb.possible = set(self.possible_words)
                ai_guess = self.ai_solver.get_guess()
                self.ai_suggestion_label.config(text=f"AI Suggestion: {ai_guess}")
            else:
                self.ai_suggestion_label.config(text="AI Suggestion: None")

    def clear_all(self):
        for entry in self.green_entries:
            entry.delete(0, tk.END)
        self.green_letters = [""] * 5

        self.gray_entry.delete(0, tk.END)
        self.gray_letters = set()

        while len(self.yellow_row_widgets) > 1:
            self.remove_yellow_row(len(self.yellow_row_widgets) - 1)

        first_row = self.yellow_row_widgets[0]
        first_row['letter_entry'].delete(0, tk.END)
        for var in first_row['position_vars']:
            var.set(False)

        self.update_possible_words()

        self.ai_suggestion_label.config(text="AI Suggestion: None")

    def make_ai_guess(self):
        """Make a guess using AI suggestion"""
        if len(self.possible_words) == 0:
            messagebox.showwarning("Warning", "No possible words left!")
            return

        ai_guess = self.ai_solver.get_guess()
        if ai_guess and "ERROR" not in ai_guess:
            success, feedback = self.game.make_guess(ai_guess)
            if success:
                # Update helper with this feedback
                self.process_feedback(ai_guess, feedback)
                self.display_board()
                self.update_possible_words()
                messagebox.showinfo("Guess Made",
                                    f"AI guessed '{ai_guess}'!\nFeedback: {self.get_colored_feedback(feedback)}")
            else:
                messagebox.showerror("Error", f"Guess failed: {feedback}")
        else:
            messagebox.showerror("Error", "AI could not generate a guess.")

    def process_feedback(self, guess: str, feedback: List[Tuple[str, str]]):
        """Process feedback to update green/yellow/gray inputs"""
        for i, (letter, color) in enumerate(feedback):
            if color == 'green':
                self.green_entries[i].delete(0, tk.END)
                self.green_entries[i].insert(0, letter)
            elif color == 'yellow':
                # Add to first yellow row or create new
                if len(self.yellow_row_widgets) == 1 and not self.yellow_row_widgets[0]['letter_entry'].get():
                    self.yellow_row_widgets[0]['letter_entry'].insert(0, letter)
                    self.yellow_row_widgets[0]['position_vars'][i].set(True)
                else:
                    self.add_yellow_row()
                    self.yellow_row_widgets[-1]['letter_entry'].insert(0, letter)
                    self.yellow_row_widgets[-1]['position_vars'][i].set(True)
            elif color == 'gray':
                current_gray = self.gray_entry.get()
                if letter not in current_gray:
                    self.gray_entry.insert(tk.END, letter)

        self.on_gray_change()  # Update gray set

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

    def display_board(self):
        """Display the game board in the GUI"""
        self.game_display.delete(1.0, tk.END)
        self.game_display.insert(tk.END, self.game.get_colored_feedback(
            self.game.feedback_history[-1]) if self.game.feedback_history else "No guesses yet.")
        self.game_display.insert(tk.END, f"\nAttempts: {len(self.game.attempts)}/6")
        if self.game.game_over:
            self.game_display.insert(tk.END, f"\n{self.game.secret_word}")

    def new_game(self):
        self.game = WordleGame(self.all_words)
        self.clear_all()
        self.display_board()

    def run(self):
        """Start the application"""
        self.root.mainloop()


# Main execution
if __name__ == "__main__":
    helper = WordleHelper("wordle_answers.txt")  # Use your word list
    helper.run()
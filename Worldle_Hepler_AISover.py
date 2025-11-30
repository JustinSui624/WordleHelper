# Worldle_Hepler_AISover.py (Dual Mode)

import random
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import List, Tuple
from pathlib import Path
import json

# ==============================================================================
# 0. MODULE IMPORTS (CRITICAL: Ensure these files are present)
# ==============================================================================
try:
    from config import MAX_GUESSES
    from solver import WordleSolver
except ImportError:
    # Fallback to prevent crash if modules are missing
    MAX_GUESSES = 6


    class WordleSolver:
        def __init__(self): raise NotImplementedError("Solver files not found.")

# --- Helper map for displaying feedback ---
COLOR_MAP = {
    'G': '#6AAA64',  # Green
    'Y': '#C9B458',  # Yellow
    'B': '#787C7E',  # Gray/Black
    'DEFAULT': '#D3D6DA',  # Light Gray/White
}


# ==============================================================================
# 7. TKINTER UI INTEGRATION (WordleHelper)
# ==============================================================================

class WordleHelper:
    def __init__(self):
        # Start in Helper Mode by default (answer=None)
        self.ai_solver = WordleSolver()
        self.ai_solver.start_game(answer=None)
        self.board_tiles: List[List[tk.Label]] = []
        self.feedback_history: List[Tuple[str, str]] = []

        self.setup_gui()
        self.display_results()
        self.update_guess_label()
        self.update_mode_display()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Wordle AI Solver (Dual Mode)")
        self.root.geometry("1000x800")

        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        input_frame = ttk.Frame(self.root, padding="15")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        input_frame.columnconfigure(0, weight=1)

        row_idx = 0

        ttk.Label(input_frame, text="WORDLE AI SOLVER", font=("Arial", 18, "bold")).grid(row=row_idx, column=0,
                                                                                         pady=(0, 15));
        row_idx += 1

        # Game Mode Display
        self.mode_label = ttk.Label(input_frame, text="", font=("Arial", 12, "bold"))
        self.mode_label.grid(row=row_idx, column=0, sticky=tk.W, pady=(0, 10));
        row_idx += 1

        game_frame = ttk.LabelFrame(input_frame, text="Game Board History", padding="10")
        game_frame.grid(row=row_idx, column=0, sticky=(tk.W, tk.E), pady=(0, 15));
        row_idx += 1
        self.setup_play_board(game_frame)

        control_frame = ttk.LabelFrame(input_frame, text="Controls & Input", padding="10")
        control_frame.grid(row=row_idx, column=0, sticky=(tk.W, tk.E), pady=(0, 15));
        row_idx += 1
        self.setup_control_section(control_frame)

        results_frame = ttk.LabelFrame(self.root, text="Possible Words & AI Suggestion", padding="15")
        results_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.setup_results_section(results_frame)

    def setup_play_board(self, parent):
        board_frame = ttk.Frame(parent)
        board_frame.grid(row=0, column=0)

        self.board_tiles = []
        for r in range(MAX_GUESSES):
            row_tiles = []
            for c in range(5):
                tile = tk.Label(board_frame, text="", font=("Arial", 24, "bold"), width=3, height=1,
                                bg=COLOR_MAP['DEFAULT'], fg='black', borderwidth=2, relief="solid")
                tile.grid(row=r, column=c, padx=3, pady=3)
                row_tiles.append(tile)
            self.board_tiles.append(row_tiles)

        self.board_status_label = ttk.Label(parent, text="Start a new game to begin.", font=("Arial", 10))
        self.board_status_label.grid(row=1, column=0, columnspan=5, pady=(5, 0))

    def setup_control_section(self, parent):
        self.ai_suggestion_label = ttk.Label(parent, text="AI Guess: ---", font=("Arial", 16, "bold"),
                                             foreground="#4C78A8")
        self.ai_suggestion_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        # --- Feedback Input (Re-enabled for Helper Mode) ---
        ttk.Label(parent, text="Feedback (G, Y, B):").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.feedback_entry = ttk.Entry(parent, width=10)
        self.feedback_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        # Action Buttons
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

        # Single Submit Button
        self.submit_button = ttk.Button(button_frame, text="✅ Submit Move", command=self.submit_move)
        self.submit_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Mode Selection Buttons
        mode_frame = ttk.Frame(parent)
        mode_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Button(mode_frame, text="✍️ Start Helper Mode", command=self.start_helper_mode).pack(side=tk.LEFT,
                                                                                                 expand=True, fill=tk.X,
                                                                                                 padx=2)
        ttk.Button(mode_frame, text="🤖 Start Engine Mode", command=self.start_engine_mode).pack(side=tk.LEFT,
                                                                                                expand=True, fill=tk.X,
                                                                                                padx=2)
        ttk.Button(mode_frame, text="▶️ Demo (SLATE)", command=lambda: self.start_engine_mode("SLATE")).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=2)

    def setup_results_section(self, parent):
        self.count_label = ttk.Label(parent, text="0 possible words", font=("Arial", 14))
        self.count_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.results_text = scrolledtext.ScrolledText(parent, width=50, height=5, font=("Consolas", 12))
        self.results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

    def update_mode_display(self):
        """Updates the label and input field state based on the current mode."""
        # Check if a secret answer is set (Engine Mode)
        if self.ai_solver.answer:
            mode_text = f"MODE: Engine (Secret: {self.ai_solver.answer})"
            color = '#4C78A8'  # Blue
            self.feedback_entry.config(state='disabled')  # Disable input
            self.submit_button.config(text="🤖 AI Make Move (Auto Feedback)")
        else:
            mode_text = "MODE: Helper (No Secret Word)"
            color = '#6AAA64'  # Green
            self.feedback_entry.config(state='normal')  # Enable input
            self.submit_button.config(text="✅ Submit Feedback")

        self.mode_label.config(text=mode_text, foreground=color)

    def update_guess_label(self):
        """Displays the AI's current best guess and saves it for the next submission."""
        next_guess = "---"
        if not self.ai_solver.game_over:
            next_guess = self.ai_solver.get_guess()
            self.ai_solver.last_guess = next_guess
            self.feedback_entry.delete(0, tk.END)

        self.ai_suggestion_label.config(text=f"AI Guess: {next_guess}")

    def submit_move(self):
        """Handles both Helper Mode (user input) and Engine Mode (auto-feedback)."""
        if self.ai_solver.game_over:
            messagebox.showwarning("Game Over", "Start a new game to continue.")
            return

        feedback_input = self.feedback_entry.get().strip()

        # Check if we are in Helper Mode and input is missing
        if not self.ai_solver.answer and not feedback_input:
            messagebox.showerror("Input Error", "In Helper Mode, you must enter the 5-char feedback (G/Y/B).")
            return

        # Pass feedback_input for Helper Mode, or empty string "" for Engine Mode
        feedback_to_solver = feedback_input if not self.ai_solver.answer else ""

        try:
            result = self.ai_solver.submit_feedback(feedback_to_solver)

            self.feedback_history.append((result["guess"], result["feedback"]))
            self.display_board()
            self.display_results()

            if result["solved"]:
                answer_display = f"Word was: {result['guess']}" if self.ai_solver.answer else "Solved!"
                messagebox.showinfo("Game Over", f"🎉 AI SOLVED IT in {self.ai_solver.turn} attempts! {answer_display}")
            elif self.ai_solver.game_over:
                answer_display = f"Word was: {self.ai_solver.answer}" if self.ai_solver.answer else "Out of guesses."
                messagebox.showinfo("Game Over", f"💀 AI ran out of guesses! {answer_display}")
            else:
                self.update_guess_label()

        except ValueError as e:
            messagebox.showerror("Solver Error", str(e))
        except Exception as e:
            messagebox.showerror("System Error", f"An unexpected error occurred: {e}")

    # --- Mode Switching Functions ---

    def start_helper_mode(self):
        """Starts a game where the AI suggests and the user provides feedback (No secret word)."""
        self.ai_solver.start_game(answer=None)  # Answer is explicitly set to None
        self.feedback_history = []

        self.display_board()
        self.display_results()
        self.update_guess_label()
        self.update_mode_display()

        self.board_status_label.config(text=f"Turn 1 of {MAX_GUESSES} (Helper Mode)", foreground='green')

    def start_engine_mode(self, word: str = None):
        """Starts a game where the AI automatically calculates feedback (Game Engine)."""

        # If no word is specified (New Game), choose a random one.
        if not word:
            word = random.choice(self.ai_solver.kb.answers)  # Get a random word

        self.ai_solver.start_game(answer=word)
        self.feedback_history = []

        self.display_board()
        self.display_results()
        self.update_guess_label()
        self.update_mode_display()

        self.board_status_label.config(text=f"Turn 1 of {MAX_GUESSES} (Engine Mode)", foreground='blue')

    def display_results(self):
        self.results_text.delete(1.0, tk.END)

        possible_words = self.ai_solver.kb.possible
        count = len(possible_words)

        self.count_label.config(text=f"📚 {count} possible words")

        if count == 0:
            self.results_text.insert(tk.END, "❌ No words match the game history!")
            self.ai_suggestion_label.config(text="AI Guess: ERROR")
        else:
            display_words = sorted(list(possible_words))
            words_per_line = 6
            for i, word in enumerate(display_words):
                self.results_text.insert(tk.END, word.ljust(6))
                if (i + 1) % words_per_line == 0:
                    self.results_text.insert(tk.END, '\n')
                else:
                    self.results_text.insert(tk.END, '  ')

    def display_board(self):
        for r in range(MAX_GUESSES):
            for c in range(5):
                self.board_tiles[r][c].config(text="", bg=COLOR_MAP['DEFAULT'], fg='black')

        for r, (guess, feedback) in enumerate(self.feedback_history):
            for c in range(5):
                color = feedback[c]
                self.board_tiles[r][c].config(text=guess[c], bg=COLOR_MAP[color],
                                              fg='white' if color != 'DEFAULT' else 'black')

        if self.ai_solver.game_over:
            status = "🎉 SOLVED!" if self.feedback_history[-1][1] == "GGGGG" else "💀 GAME OVER!"

            if self.ai_solver.answer:
                status += f" (Word: {self.ai_solver.answer})"

            self.board_status_label.config(text=status,
                                           foreground='red' if not self.feedback_history[-1][1] == "GGGGG" else 'green')
        else:
            mode_desc = "Engine Mode" if self.ai_solver.answer else "Helper Mode"
            self.board_status_label.config(text=f"Turn {self.ai_solver.turn + 1} of {MAX_GUESSES} ({mode_desc})",
                                           foreground='black')

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    helper = WordleHelper()
    helper.run()
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from typing import List, Set, Dict
import WordleAI.py as wordleai
try:
    from wordleai import EntropyAI, ReinforcementAI, WordleAITrainer
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("Warning: wordleai.py not found. AI recommendations will not be available.")

class WordleHelper:
    def __init__(self, word_list_path: str = "word_list.txt"):
        self.all_words = self.load_words_from_file(word_list_path)
        if not self.all_words:
            self.all_words = self.get_default_word_list()
        
        self.possible_words = self.all_words.copy()
        self.green_letters = [""] * 5
        self.yellow_letters = []
        self.gray_letters = set()
        self.yellow_rows = 1
        
        self.ai = None
        if AI_AVAILABLE:
            try:
                self.ai = EntropyAI(self.all_words)
            except:
                self.ai = None
        
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
        return ["APPLE", "BRAVE", "CLIMB", "DREAM", "EARTH", "FLAME", "GRAPE", "HOUSE"]
    
    def setup_gui(self):
        """Create the main interface"""
        self.root = tk.Tk()
        self.root.title("Wordle Helper")
        self.root.geometry("800x700")
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(main_frame, text="Wordle Helper", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        green_frame = ttk.LabelFrame(main_frame, text="🟩 Green Letters (Correct Position)", padding="10")
        green_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        green_frame.columnconfigure(0, weight=1)
        
        self.setup_green_section(green_frame)
        
        yellow_frame = ttk.LabelFrame(main_frame, text="🟨 Yellow Letters (Wrong Position)", padding="10")
        yellow_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        yellow_frame.columnconfigure(1, weight=1)
        
        self.setup_yellow_section(yellow_frame)
        
        gray_frame = ttk.LabelFrame(main_frame, text="⬜ Gray Letters (Not in Word)", padding="10")
        gray_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        gray_frame.columnconfigure(0, weight=1)
        
        self.setup_gray_section(gray_frame)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(control_frame, text="Update Results", command=self.update_possible_words).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Add Yellow Row", command=self.add_yellow_row).pack(side=tk.LEFT, padx=5)
        
        results_frame = ttk.LabelFrame(main_frame, text="Possible Words", padding="10")
        results_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        self.setup_results_section(results_frame)
        
        if AI_AVAILABLE and self.ai:
            ai_frame = ttk.LabelFrame(main_frame, text="🤖 AI Recommendation", padding="10")
            ai_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
            
            self.ai_label = ttk.Label(ai_frame, text="Recommended next word will appear here", font=("Arial", 12, "bold"))
            self.ai_label.grid(row=0, column=0, sticky=tk.W)
            
            ttk.Button(ai_frame, text="Get AI Recommendation", command=self.get_ai_recommendation).grid(row=0, column=1, padx=10)
    
    def setup_green_section(self, parent):
        """Setup the green letters input boxes"""
        green_subframe = ttk.Frame(parent)
        green_subframe.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.green_entries = []
        for i in range(5):
            label = ttk.Label(green_subframe, text=f"Position {i+1}:")
            label.grid(row=0, column=i*2, padx=(10, 5), pady=5)
            
            entry = ttk.Entry(green_subframe, width=3, font=("Arial", 14), justify='center')
            entry.grid(row=0, column=i*2+1, padx=(0, 10), pady=5)
            entry.bind('<KeyRelease>', lambda e, pos=i: self.on_green_change(pos))
            self.green_entries.append(entry)
    
    def setup_yellow_section(self, parent):
        """Setup the yellow letters input section with multiple rows"""
        self.yellow_frame_container = ttk.Frame(parent)
        self.yellow_frame_container.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.yellow_rows_frame = ttk.Frame(self.yellow_frame_container)
        self.yellow_rows_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.yellow_row_widgets = []
        
        self.add_yellow_row()
    
    def add_yellow_row(self):
        """Add a new row for yellow letters"""
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
            check = ttk.Checkbutton(row_frame, text=str(i+1), variable=var)
            check.grid(row=0, column=3+i, padx=2)
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
        """Remove a yellow letter row"""
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
        """Setup the gray letters input"""
        gray_subframe = ttk.Frame(parent)
        gray_subframe.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.gray_entry = ttk.Entry(gray_subframe, width=30, font=("Arial", 12))
        self.gray_entry.grid(row=0, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        self.gray_entry.bind('<KeyRelease>', lambda e: self.on_gray_change())
        
        gray_help = ttk.Label(gray_subframe, text="Enter all gray letters (no spaces)")
        gray_help.grid(row=1, column=0, sticky=tk.W, padx=10)
    
    def setup_results_section(self, parent):
        """Setup the results display"""

        self.count_label = ttk.Label(parent, text="0 possible words", font=("Arial", 12, "bold"))
        self.count_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.results_text = scrolledtext.ScrolledText(parent, width=80, height=15, font=("Consolas", 10))
        self.results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
    
    def on_green_change(self, position):
        """Handle green letter input changes"""
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
        """Handle gray letters input changes"""
        text = self.gray_entry.get().upper()
        
        filtered_text = ''.join([c for c in text if c.isalpha()])
        if filtered_text != text:
            self.gray_entry.delete(0, tk.END)
            self.gray_entry.insert(0, filtered_text)
            text = filtered_text
        
        self.gray_letters = set(text)
        self.update_possible_words()
    
    def update_yellow_letters(self):
        """Update yellow letters from all rows"""
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
        """Update the list of possible words based on current constraints"""
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
        """Display the possible words in the results area"""
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
    
    def get_ai_recommendation(self):
        """Get AI recommendation for next word"""
        if not AI_AVAILABLE or not self.ai:
            messagebox.showerror("Error", "AI not available. Make sure wordleai.py is in the same directory.")
            return
        
        try:
            self.ai.reset()

            if self.possible_words:
                if hasattr(self.ai, 'get_best_guess'):
                    recommendation = self.ai.get_best_guess()
                else:
                    top_candidates = self.possible_words[:10]
                    recommendation = max(top_candidates, key=lambda word: len(set(word)))
                
                self.ai_label.config(text=f"Recommended: {recommendation}")
            else:
                self.ai_label.config(text="No words available for recommendation")
                
        except Exception as e:
            messagebox.showerror("Error", f"AI recommendation failed: {str(e)}")
    
    def clear_all(self):
        """Clear all inputs"""
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
        
        if AI_AVAILABLE and self.ai:
            self.ai_label.config(text="Recommended next word will appear here")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    helper = WordleHelper("word_list.txt")
    helper.run()

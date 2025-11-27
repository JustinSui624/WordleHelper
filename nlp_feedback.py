import re


def parse_feedback(text: str) -> str:
    """
    Validates and cleans user input (e.g., 'G Y B B Y') into a strict 5-character
    Wordle feedback string (e.g., 'GYBBY').
    """
    text = text.upper().strip()

    # 1. Check for the perfect, desired format
    if re.match(r'^[GYB]{5}$', text):
        return text

    # 2. Sanitize and Map common typos/variations
    # This mapping converts any extra letters the user might type into 'B' (Gray)
    # as a fallback, and removes spaces.
    mapping = {'A': 'B', 'C': 'B', 'D': 'B', 'F': 'B', 'H': 'B', 'J': 'B',
               'K': 'B', 'L': 'B', 'M': 'B', 'O': 'B', 'P': 'B', 'Q': 'B',
               'R': 'B', 'S': 'B', 'T': 'B', 'U': 'B', 'V': 'B', 'W': 'B',
               'X': 'B', 'Z': 'B',
               'G': 'G', 'Y': 'Y', 'B': 'B', ' ': '', '_': 'B'}

    # Filter out spaces and map remaining characters
    filtered_text = "".join(mapping.get(c, 'B') for c in text if c != ' ')

    # Ensure the string is exactly 5 characters long
    sanitized = filtered_text[:5].ljust(5, 'B')

    if len(sanitized) != 5 or not re.match(r'^[GYB]{5}$', sanitized):
        # This part should theoretically be unreachable after ljust(5, 'B')
        raise ValueError(f"Invalid feedback '{text}'. Use exactly 5 chars: G (green), Y (yellow), B (gray).")

    return sanitized
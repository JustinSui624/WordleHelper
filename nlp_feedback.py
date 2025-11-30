import re


def parse_feedback(text: str) -> str:
    text = text.upper().strip()
    if re.match(r'^[GYB]{5}$', text):
        return text

    # Full sanitization mapping for robustness
    mapping = {'G': 'G', 'Y': 'Y', 'B': 'B', ' ': '', '_': 'B'}

    # Filter out spaces and map remaining characters
    filtered_text = "".join(mapping.get(c, 'B') for c in text if c != ' ')

    # Ensure the string is exactly 5 characters long
    sanitized = filtered_text[:5].ljust(5, 'B')

    if len(sanitized) != 5 or not re.match(r'^[GYB]{5}$', sanitized):
        raise ValueError(f"Invalid feedback '{text}'. Use exactly 5 chars: G (green), Y (yellow), B (gray).")

    return sanitized
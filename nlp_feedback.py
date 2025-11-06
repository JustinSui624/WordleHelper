import re

def parse_feedback(text: str) -> str:
    text = text.upper().strip()
    if re.match(r'^[GYB]{5}$', text):
        return text

    # Sanitize: Map common typos/variations (e.g., 'g'→'G', 'y'→'Y', 'b'→'B')
    mapping = {'A': 'B', 'C': 'B', 'G': 'G', 'Y': 'Y', 'B': 'B', ' ': 'B', '_': 'B'}
    sanitized = ''.join(mapping.get(c, 'B') for c in text[:5]).ljust(5, 'B')[:5]

    if len(sanitized) < 5 or not re.match(r'^[GYB]{5}$', sanitized):
        raise ValueError(f"Invalid feedback '{text}'. Use 5 chars: G (green), Y (yellow), B (gray).")

    return sanitized
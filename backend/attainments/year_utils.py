import re


def previous_academic_year(year):
    """Turn 2024-25 into 2023-24, or 2024-2025 into 2023-2024."""
    text = (year or '').strip()
    match = re.match(r'^(\d{4})\s*([-/])\s*(\d{2,4})$', text)
    if not match:
        return None
    start = int(match.group(1))
    sep = match.group(2)
    end = match.group(3)
    prev_start = start - 1
    if len(end) == 2:
        prev_end = f'{(int(end) - 1) % 100:02d}'
    else:
        prev_end = str(int(end) - 1)
    return f'{prev_start}{sep}{prev_end}'

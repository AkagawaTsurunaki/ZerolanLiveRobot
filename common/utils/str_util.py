import re


def is_blank(s: str) -> bool:
    """Check if a string is None, empty, or contains only whitespace."""
    return s is None or not s.strip() or s == ""


def split_by_punctuations(text, punctuations=None, k=10):
    if punctuations is None:
        punctuations = ["：", "。", "！", "？", "!", "?"]
    pattern = '|'.join(re.escape(p) for p in punctuations)
    parts = re.split(pattern, text)
    parts = [part for part in parts if part.strip()]

    return parts


def adjust_strings(strings, k):
    adjusted_strings = []
    i = 0
    while i < len(strings):
        current_str = strings[i]

        # Check if current string meets the length requirement
        if len(current_str) > k:
            adjusted_strings.append(current_str)
            i += 1
        else:
            # Combine with the previous string if possible
            if i > 0:
                previous_str = adjusted_strings.pop()
                combined_str = previous_str + current_str
                adjusted_strings.append(combined_str)
                i += 1
            else:
                # If no previous string to combine with, combine with the next one
                if i < len(strings) - 1:
                    next_str = strings[i + 1]
                    combined_str = current_str + next_str
                    adjusted_strings.append(combined_str)
                    i += 2  # Move to the string after next
                else:
                    # If it's the last string and still not adjusted, just append
                    adjusted_strings.append(current_str)
                    i += 1

    return adjusted_strings

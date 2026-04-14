import re
from typing import List, Optional

from common.enumerator import Language


def is_blank(s: str) -> bool:
    """Check if a string is None, empty, or contains only whitespace."""
    return s is None or not s.strip() or s == ""


def split_by_punc(text: str, lang: Language) -> List[str]:
    if lang == Language.ZH:
        cut_punc = "，。！？"
    elif lang == Language.JA:
        cut_punc = "、。！？"
    else:
        cut_punc = ",.!?"

    def punc_cut(text: str, punc: str):
        texts = []
        last = -1
        for i in range(len(text)):
            if text[i] in punc:
                try:
                    texts.append(text[last + 1: i])
                except IndexError:
                    continue
                last = i
        return texts

    return punc_cut(text, cut_punc)


def remove_md_blocks(text: Optional[str]) -> Optional[str]:
    """
    Remove Markdown blocks from a string.
    More cases in `tests/common/test_str_util.py`
    """
    if not text:
        return text

    text = text.strip()

    pattern = r'^```[\w]*\n?(.*?)\n?```$'
    match = re.match(pattern, text, re.DOTALL)

    if match:
        return match.group(1).strip()
    return text

import json
import re
from json import JSONDecodeError


def _extract_json_from_markdown(markdown_text: str) -> str:
    cleaned_text = re.sub(r'```.*?\n(.*?)\n```', r'\1', markdown_text, flags=re.DOTALL)
    return cleaned_text


def _remove_extra_braces(json_string):
    for i in range(len(json_string) - 1, 0, -1):
        if json_string[i] == '}':
            json_string = json_string[:i] + json_string[i + 1:]
            return json_string


def _normal_load(content: str):
    return json.loads(content)


def _md_load(content: str):
    content = _extract_json_from_markdown(content)
    return _normal_load(content)


def _ebr_load(content: str):
    content = _remove_extra_braces(content)
    return _normal_load(content)


def _md_ebr_load(content: str):
    content = _extract_json_from_markdown(content)
    content = _remove_extra_braces(content)
    return _normal_load(content)


_strategies = [_normal_load, _md_load, _ebr_load, _md_ebr_load]


def smart_load_json_like(content: str):
    errs = []
    for strategy in _strategies:
        try:
            return strategy(content)
        except JSONDecodeError as e:
            errs.append(e)
    raise errs[-1]

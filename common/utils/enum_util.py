from enum import Enum
from typing import Type, Any, List

from typeguard import typechecked


def enum_members_to_list(enum: Type[Enum]) -> List[Any]:
    return [member.value for member in enum]


@typechecked
def enum_members_to_str_list(enum: Type[Enum]) -> List[str]:
    return [str(elm.value) for elm in list(enum)]


@typechecked
def _enum_members_to_plain_text_with_comma(enum: Type[Enum]) -> str:
    str_list = enum_members_to_str_list(enum)
    text = ""
    for string in str_list:
        text += "`" + string + "`" + ", "
    return text[:-2]


@typechecked
def enum_to_markdown(enum: Type[Enum]) -> str:
    num_of_enum = len(enum)
    if num_of_enum == 1:
        return f"`{list(enum)[0].value}` is supported only."
    else:
        candidates = _enum_members_to_plain_text_with_comma(enum)
        return f"{candidates} are supported."

@typechecked
def enum_to_markdown_zh(enum: Type[Enum]) -> str:
    num_of_enum = len(enum)
    if num_of_enum == 1:
        return f"仅支持 `{list(enum)[0].value}`。"
    else:
        candidates = _enum_members_to_plain_text_with_comma(enum)
        return f"支持 {candidates}。"
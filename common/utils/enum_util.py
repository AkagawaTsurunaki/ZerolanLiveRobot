from enum import Enum
from typing import Type, Any, List

from typeguard import typechecked


def enum_members_to_list(enum: Type[Enum]) -> List[Any]:
    return [member.value for member in enum]

@typechecked
def enum_members_to_str_list(enum: Type[Enum]) -> List[str]:
    return [str(elm.value) for elm in list(enum)]

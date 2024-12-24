from enum import Enum
from typing import Type


def enum_members_to_list(enum: Type[Enum]):
    return [member.value for member in enum]

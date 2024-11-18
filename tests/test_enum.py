from enum import Enum

from pydantic import BaseModel


class AEnum(str, Enum):
    abs = "abs"
    ami = "ami"

class BClass(BaseModel):
    name: str
    enum: AEnum


b = BClass(name="sss", enum=AEnum.abs)

b_ = {
    "name": "asasa",
    "enum": "ami"
}

c = BClass.model_validate(b_)

print(c)
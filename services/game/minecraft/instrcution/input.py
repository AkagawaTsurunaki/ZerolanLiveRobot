from dataclasses import dataclass
from typing import Optional, Union

from dataclasses_json import dataclass_json
from pydantic import create_model, Field


def ts_type_to_py_type(t: str) -> type:
    if t == 'number':
        return Union[float, int]
    elif t == 'string':
        return str
    elif t == 'boolean':
        return bool
    else:
        raise ValueError(f"Not a valid type: {t}")


@dataclass_json
@dataclass
class FieldMetadata:
    name: str
    type: str
    description: str
    required: bool


def generate_model_from_args(args_list: list[FieldMetadata]):
    fields = {}
    for arg in args_list:
        name = arg.name
        assert isinstance(name, str)
        field_type = arg.type
        assert isinstance(field_type, str)
        field_type = ts_type_to_py_type(field_type)
        required = arg.required
        assert isinstance(required, bool)
        description = arg.description
        assert isinstance(description, str)

        if required:
            fields[name] = (field_type, Field(default=None, description=description))
        else:
            fields[name] = (Optional[field_type], Field(default=None, description=description))

    return create_model('DynamicModel', **fields)


# # 示例JSON对象
# json_object = {
#     'args': [
#         {'name': 'id', 'description': 'The identifier', 'type': 'number', 'required': True},
#         {'name': 'name', 'description': 'The name', 'type': 'string', 'required': False},
#         {'name': 'isBot', 'description': 'Are you a robot?', 'type': 'boolean', 'required': True},
#     ]
# }
#
# # 调用函数生成模型
# DynamicModel = generate_model_from_args(json_object['args'])
# print(DynamicModel)

from dataclasses import dataclass
from typing import Optional, Union

from dataclasses_json import dataclass_json
from pydantic import create_model, Field, BaseModel


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


def generate_model_from_args(class_name: str, args_list: list[FieldMetadata]):
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

    model = create_model(class_name, **fields)
    assert issubclass(model, BaseModel)
    return model


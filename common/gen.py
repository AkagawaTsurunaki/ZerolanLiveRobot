from pydantic import BaseModel
from pydantic.fields import FieldInfo


class ConfigFileGenerator:

    def __init__(self, indent: int = 2):
        self._yaml_str = ""
        self._indent = indent

    def _get_indent(self, depth: int):
        return " " * self._indent * depth

    def _add_comments(self, field_info: FieldInfo, depth: int):
        if field_info.description:
            for description_line in field_info.description.split("\n"):
                self._yaml_str += self._get_indent(depth) + f"# {description_line}\n"

    def _gen(self, model: BaseModel, depth: int = 0) -> str:
        fields = model.model_fields

        for field_name, field_info in fields.items():
            field_val = model.__getattribute__(field_name)
            if isinstance(field_val, BaseModel):
                self._add_comments(field_info, depth)
                self._yaml_str += self._get_indent(depth) + f"{field_name}:\n"
                self._gen(field_val, depth + 1)
            else:
                self._add_comments(field_info, depth)
                if isinstance(field_val, str):
                    self._yaml_str += self._get_indent(depth) + f"{field_name}: '{field_val}'\n"
                else:
                    self._yaml_str += self._get_indent(depth) + f"{field_name}: {field_val}\n"
        return self._yaml_str

    def generate_yaml(self, model: BaseModel):
        """
        Generate yaml from BaseModel instance.
        :param model: An instance of BaseModel.
        :return: Yaml string.
        """
        assert model, f"None can not be generated."
        return self._gen(model, depth=0)

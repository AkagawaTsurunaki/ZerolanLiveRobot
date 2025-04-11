from datetime import datetime

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from typeguard import typechecked

from common import ver_check
from common.decorator import log_run_time


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

    def _gen(self, model: BaseModel, depth: int = 0):
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

    def _get_header(self):
        now = datetime.now()
        formatted_date = now.isoformat()

        generated_info = f"# This file was generated at {formatted_date} #"
        header = "#" * len(generated_info) + "\n" \
                 + generated_info + "\n" \
                 + "#" * len(generated_info) + "\n"

        return header

    @log_run_time()
    @typechecked
    def generate_yaml(self, model: BaseModel):
        """
        Generate yaml from BaseModel instance.
        :param model: An instance of BaseModel.
        :return: Yaml string.
        """
        ver_check.check_pydantic_ver()
        self._gen(model, depth=0)
        return self._get_header() + "\n" + self._yaml_str

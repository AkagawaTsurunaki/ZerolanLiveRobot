import typing
from enum import Enum
from typing import Any, Union, List, Tuple, Callable

import gradio as gr
from loguru import logger
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from typeguard import typechecked

from common import ver_check
from common.utils.enum_util import enum_members_to_str_list
from event.event_data import ConfigFileModifiedEvent
from event.event_emitter import emitter
from manager.config_manager import save_config

"""
Analyse config schema of the project and automatically generate config WebUI page using gradio.
"""


def _add_field_component(field_info: FieldInfo, field_name: str, field_val: Any) -> gr.Component:
    """
    Convert Pydantic field type to appropriate Gradio component.
    Note: Should not call component.add() method again, because the context manager will handle it automatically.
          Or it will cause duplicated components.
    :param field_info: FieldInfo instance.
    :param field_name: Field name.
    :param field_val: Value of the field.
    :return: Gradio component.
    """
    comp = None
    field_type = field_info.annotation
    field_desc = field_info.description
    interactive = not field_info.frozen

    if field_type == str or (field_type == Union[str | None]):
        comp = gr.Textbox(label=field_name, info=field_desc, value=field_val, interactive=interactive)
    elif field_type == int:
        comp = gr.Number(label=field_name, info=field_desc, value=field_val, interactive=interactive)
    elif field_type == float:
        comp = gr.Number(label=field_name, info=field_desc, value=field_val, interactive=interactive)
    elif field_type == bool:
        comp = gr.Checkbox(label=field_name, info=field_desc, value=field_val, interactive=interactive)
    elif isinstance(field_val, Enum):
        choices = enum_members_to_str_list(type(field_val))
        comp = gr.Dropdown(label=field_name, info=field_desc, value=field_val.value, choices=choices, interactive=interactive)
    elif field_type == list or field_type == typing.List[str]:
        assert isinstance(field_val, list)
        str_list = [[str(elm)] for elm in field_val]
        gr.List(label=field_name, value=str_list)
    else:
        logger.warning(f"Field {field_name} with type {field_type} not supported.")
    return comp


class DynamicConfigPage:
    def __init__(self, model: BaseModel):
        self.model: BaseModel = model
        self._theme = gr.themes.Soft()
        self.blocks = gr.Blocks(theme=self._theme)
        self.input_comps = []
        self.assign_funcs: List[Tuple[Callable, BaseModel, str, FieldInfo]] = []
        self._field_setters: List[FieldSetter] = []

    @typechecked
    def launch(self, share: bool = False):
        """
        Launch the Gradio interface.
        """
        # Add components based on model fields
        with self.blocks:
            gr.Markdown("# Config Page")
            with gr.Row():
                gr.Markdown(
                    "> This config page is generated from the config schema of the current version of ZerolanLiveRobot.\n"
                    "> You can also modify the saved config file at `resource/config.yaml` manually.")
                btn = gr.Button("Save Config")

                def on_click(*args):
                    assert len(args) == len(self.input_comps) == len(self._field_setters)
                    for setter, arg in zip(self._field_setters, args):
                        setter.set_field(arg)
                    try:
                        save_config(self.model)
                        gr.Info("Config file saved.")
                        emitter.emit(ConfigFileModifiedEvent())
                    except Exception as e:
                        logger.exception(e)
                        gr.Error("Failed to save config file.")

                btn.click(on_click, inputs=self.input_comps)
            self._add_block_components(self.model)
        self.blocks.launch(share)

    async def start(self):
        async def async_start():
            self.launch()

        await async_start()

    @typechecked
    def _add_block_components(self, model: BaseModel):
        """
        Add components base on model you provided.
        :param model: Instance of BaseModel
        """
        ver_check.check_pydantic_ver()

        fields = model.model_fields

        for field_name, field_info in fields.items():
            field_val = model.__getattribute__(field_name)
            if isinstance(field_val, BaseModel):
                with gr.Tab(f"{field_name}"):
                    with gr.Blocks():
                        gr.Markdown(field_info.description)
                        self._add_block_components(field_val)
            else:
                frozen = field_info.frozen
                comp = _add_field_component(field_info, field_name, field_val)
                if comp is not None:
                    if not frozen:
                        self.input_comps.append(comp)
                        self._field_setters.append(FieldSetter(model, field_name))


class FieldSetter:
    def __init__(self, model: BaseModel, field_name: str):
        ver_check.check_pydantic_ver()
        self._model = model
        self._field_name = field_name

    def _field_convert(self, field_name: str, val: Union[str, List[List[str]]]):
        """
        Convert value to fit target type of field.
        Note: This method will not really set the target field.
        :param field_name: Field name.
        :param val: Field value to convert.
        :return: Converted value.
        """
        field_info = self._model.model_fields[field_name]
        field_type = field_info.annotation
        if issubclass(type(field_type), type(Enum)):
            res = field_type(val)
        elif field_type == List[str]:
            res = []
            for row in val:
                for col in row:
                    assert isinstance(col, str)
                    res.append(col)
        else:
            res = val
        return res

    def set_field(self, val: Any):
        # Convert value base on the type of the field.
        field_name = self._field_name
        val = self._field_convert(field_name, val)
        # Set field.
        self._model.__setattr__(field_name, val)
        # Model Validate.
        self._model.model_validate(self._model)

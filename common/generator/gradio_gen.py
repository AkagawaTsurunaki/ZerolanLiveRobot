import typing
from enum import Enum
from typing import Any, Union

import gradio as gr
from loguru import logger
from pydantic import BaseModel
from typeguard import typechecked

from common import ver_check
from common.config import ZerolanLiveRobotConfig
from common.utils.enum_util import enum_members_to_str_list

"""
Analyse config schema of the project and automatically generate config WebUI page using gradio.
"""


def _add_field_component(field_name: str, field_type: Any, field_desc: str, field_val: Any):
    """
    Convert Pydantic field type to appropriate Gradio component.
    Note: Should not call component.add() method again, because the context manager will handle it automatically.
          Or it will cause duplicated components.
    :param field_name:
    :param field_type:
    :return:
    """
    if field_type == str or (field_type == Union[str | None]):
        gr.Textbox(label=field_name, info=field_desc, value=field_val, interactive=True)
    elif field_type == int:
        gr.Number(label=field_name, info=field_desc, value=field_val, interactive=True)
    elif field_type == float:
        gr.Number(label=field_name, info=field_desc, value=field_val, interactive=True)
    elif field_type == bool:
        gr.Checkbox(label=field_name, info=field_desc, value=field_val, interactive=True)
    elif isinstance(field_val, Enum):
        choices = enum_members_to_str_list(type(field_val))
        gr.Dropdown(label=field_name, info=field_desc, choices=choices, interactive=True)
    elif field_type == list or field_type == typing.List[str]:
        assert isinstance(field_val, list)
        str_list = [[str(elm)] for elm in field_val]
        with gr.Row():
            ls = gr.List(label=field_name, value=str_list)
            with gr.Column():
                tb = gr.Textbox(label=field_name, info=field_desc, interactive=True)

                def on_add_btn_click(text):
                    str_list.append([text])
                    return None, str_list

                btn = gr.Button(value="Add")
                btn.click(fn=on_add_btn_click, inputs=tb, outputs=[tb, ls])
    else:
        logger.warning(f"Field {field_name} with type {field_type} not supported.")


@typechecked
def _add_block_components(model: BaseModel):
    """
    Add components base on model you provided.
    :param model: Instance of BaseModel
    """
    ver_check.check_pydantic_ver()

    fields = model.model_fields

    for field_name, field_info in fields.items():
        field_val = model.__getattribute__(field_name)
        field_type = field_info.annotation
        if isinstance(field_val, BaseModel):
            with gr.Tab(f"{field_name}"):
                with gr.Blocks():
                    gr.Markdown(field_info.description)
                    _add_block_components(field_val)
        else:
            _add_field_component(field_name, field_type, field_info.description, field_val)


class DynamicConfigPage:
    def __init__(self, model: BaseModel):
        self.model: BaseModel = model
        self._theme = gr.themes.Soft()
        self.blocks = gr.Blocks(theme=self._theme)

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
                # btn.click()
            _add_block_components(self.model)
        self.blocks.launch(share)


# Create and launch the config page
config_page = DynamicConfigPage(ZerolanLiveRobotConfig())
config_page.launch()

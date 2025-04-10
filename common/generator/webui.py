from typing import Any

import gradio as gr
from loguru import logger
from pydantic import BaseModel

from common.config import ZerolanLiveRobotConfig

global_theme = gr.themes.Soft()


def _add_field_component(field_name: str, field_type: Any, field_desc, field_val: Any):
    """
    Convert Pydantic field type to appropriate Gradio component.
    Note: Should not call component.add() method again, because the context manager will handle it automatically.
          Or it will cause duplicated components.
    :param field_name:
    :param field_type:
    :return:
    """
    if field_type == str:
        gr.Textbox(label=field_name, info=field_desc, value=field_val, interactive=True)
    elif field_type == int:
        gr.Number(label=field_name, info=field_desc, value=field_val, interactive=True)
    elif field_type == float:
        gr.Number(label=field_name, info=field_desc, value=field_val, interactive=True)
    elif field_type == bool:
        gr.Checkbox(label=field_name, info=field_desc, value=field_val, interactive=True)
    elif field_type == list:
        assert isinstance(field_val, list)
        str_list = [[str(elm)] for elm in field_val]
        with gr.Row():
            gr.List(label=field_name, value=str_list)
            with gr.Column():
                gr.Textbox(label=field_name, info=field_desc, interactive=True)
                gr.Button("Add")
    else:
        logger.warning(f"Field {field_name} with type {field_type} not supported.")


def _add_block_components(blocks: gr.Blocks, model: BaseModel):
    """Add components based on model fields."""
    fields = model.model_fields

    for field_name, field_info in fields.items():
        field_val = model.__getattribute__(field_name)
        if isinstance(field_val, BaseModel):
            with gr.Tab(f"{field_name}"):
                with gr.Blocks() as child:
                    # gr.Tab(f"{field_name}")
                    gr.Markdown(field_info.description)
                    _add_block_components(child, field_val)
        else:
            _add_field_component(field_name, type(field_val), field_info.description, field_val)


class DynamicConfigPage:
    def __init__(self, model: BaseModel):
        self.model: BaseModel = model
        self.blocks = gr.Blocks(theme=global_theme)

    def launch(self):
        """Launch the Gradio interface."""
        # Add components based on model fields
        with self.blocks:
            gr.Markdown("# Config Page")
            gr.Markdown(
                "> This config page is generated from the config schema of the current version of ZerolanLiveRobot.\n"
                "> You can also modify the saved config file at `resource/config.yaml` manually.")
            _add_block_components(self.blocks, self.model)
        self.blocks.launch(share=False)


# Create and launch the config page
config_page = DynamicConfigPage(ZerolanLiveRobotConfig())
config_page.launch()

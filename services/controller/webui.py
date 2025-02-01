import gradio as gr
from gradio.components.textbox import Textbox

from common.abs_runnable import AbstractRunnable
from services.controller.controller import ZerolanController


class ZerolanControllerWebUI(AbstractRunnable):

    def __init__(self, controller: ZerolanController):
        super().__init__()
        self._controller = controller
        self._history_num_text_box = None
        self._microphone_btn = None
        self._frontend = None

    def name(self):
        return "ZerolanController"

    def _webui(self):
        with gr.Blocks() as frontend:
            self._frontend = frontend
            gr.Markdown("# ZerolanController")
            with gr.Row(equal_height=True) as row:
                self._microphone_btn = gr.Button("🎙️")
                self._microphone_btn.click(self._controller.switch_microphone)
            with gr.Row(equal_height=True) as row2:
                self._history_num_text_box = Textbox("Runtime history: ?")
                self._history_num_text_box.change()

    async def start(self):
        await super().start()
        self._webui()
        self._frontend.launch()

    async def stop(self):
        await super().stop()
        self._frontend.close()

import gradio as gr

import controller.api

with gr.Blocks(theme=gr.themes.Soft()) as controller_inteface:
    gr.Markdown('# 🕹️ Zerolan Live Robot ver1.1 控制面板')
    with gr.Row():
        # gr.Chatbot(label='LLM 对话区', value=controller.api.get_history, every=1, height=800, min_width=800)

        with gr.Column():
            gr.Markdown('## 运行时控制')
            llm_reset_button = gr.ClearButton(value='🔃 重载提示词')
            audio_player_switch_btn = gr.ClearButton(value='👄 启禁用发声')
            vad_switch_btn = gr.Button(value='👂️ 启禁用听觉')
            obs_clear_btn = gr.Button(value='😀 清空 OBS 输出')
            # stop_zerolan_button = gr.Button(value='⛔️ 终止 Zerolan Live Robot')

            llm_reset_button.click(fn=controller.api.llm_reset)
            audio_player_switch_btn.click(fn=controller.api.audio_player_switch)
            vad_switch_btn.click(fn=controller.api.vad_switch)
            obs_clear_btn.click(fn=controller.api.obs_clear)

controller_inteface.launch()

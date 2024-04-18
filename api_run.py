import argparse

import asr.app
import blip_img_cap.app
import llm.chatglm3.app
import llm.qwen.app
import llm.yi_6b.app

parser = argparse.ArgumentParser(description='启动分布式服务的工具')

parser.add_argument('--service', '-s', type=str, default=False)
parser.add_argument('--model-path', '-mp', type=str, default="chatglm3")
parser.add_argument('--quantize', '-q', type=int, default=4)
parser.add_argument('--loading-mode', '-lm', type=str, default='auto')
parser.add_argument('--host', '-h', type=str, default='127.0.0.1')
parser.add_argument('--port', '-p', type=int, default=9881)
parser.add_argument('--debug', '-d', type=str, default=False)

service, model_path, quantize, loading_mode, host, port, debug = parser.parse_args()
args = parser.parse_args()

startable_service_dict = {}

if args.service:
    if service == 'asr':
        asr.app.start()
    elif service == 'blip':
        blip_img_cap.app.start()
    elif service == 'chatglm3':
        llm.chatglm3.app.start(model_path, quantize, host, port, debug)
    elif service == 'Qwen/Qwen-7B-Chat':
        llm.qwen.app.start(model_path, loading_mode, host, port, debug)
    elif service == '01-ai/Yi':
        llm.yi_6b.app.start(model_path, loading_mode, host, port, debug)

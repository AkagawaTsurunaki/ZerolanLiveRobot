import argparse

from utils.datacls import ServiceNameRegistry as SNR

parser = argparse.ArgumentParser(description='启动分布式服务的工具')

parser.add_argument('--service', type=str, default=False)
parser.add_argument('--model-path', type=str, default=SNR.CHATGLM3)
parser.add_argument('--quantize', type=int, default=4)
parser.add_argument('--loading-mode', type=str, default='auto')
parser.add_argument('--host', type=str, default='127.0.0.1')
parser.add_argument('--port', type=int, default=9881)
parser.add_argument('--debug', type=bool, default=False)

args = parser.parse_args()

startable_service_dict = {}

if args.service:
    if args.service == SNR.ASR:
        import asr.app

        asr.app.start()
    elif args.service == SNR.BLIP:
        import blip_img_cap.app

        blip_img_cap.app.start(args.model_path, args.host, args.port, args.debug)
    elif args.service == SNR.CHATGLM3:
        import llm.chatglm3.app

        llm.chatglm3.app.start(args.model_path, args.quantize, args.host, args.port, args.debug)
    elif args.service == SNR.QWEN:
        import llm.qwen.app

        llm.qwen.app.start(args.model_path, args.loading_mode, args.host, args.port, args.debug)
    elif args.service == SNR.YI:
        import llm.yi_6b.app

        llm.yi_6b.app.start(args.model_path, args.loading_mode, args.host, args.port, args.debug)
    elif args.service == SNR.SHISA:
        import llm.shisa.app

        llm.shisa.app.start(args.model_path, args.host, args.port, args.debug)

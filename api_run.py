import argparse

parser = argparse.ArgumentParser(description='启动分布式服务的工具')

parser.add_argument('--service', type=str, default=False)
parser.add_argument('--model-path', type=str, default="chatglm3")
parser.add_argument('--quantize', type=int, default=4)
parser.add_argument('--loading-mode', type=str, default='auto')
parser.add_argument('--host', type=str, default='127.0.0.1')
parser.add_argument('--port', type=int, default=9881)
parser.add_argument('--debug', type=bool, default=False)

args = parser.parse_args()

startable_service_dict = {}

if args.service:
    if args.service == 'asr':
        import asr.app

        asr.app.start()
    elif args.service == 'blip':
        import blip_img_cap.app

        blip_img_cap.app.start()
    elif args.service == 'chatglm3':
        import llm.chatglm3.app

        llm.chatglm3.app.start(args.model_path, args.quantize, args.host, args.port, args.debug)
    elif args.service == 'Qwen/Qwen-7B-Chat':
        import llm.qwen.app

        llm.qwen.app.start(args.model_path, args.loading_mode, args.host, args.port, args.debug)
    elif args.service == '01-ai/Yi':
        import llm.yi_6b.app

        llm.yi_6b.app.start(args.model_path, args.loading_mode, args.host, args.port, args.debug)

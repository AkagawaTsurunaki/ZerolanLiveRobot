import argparse

import asr.app
import blip_img_cap.app

parser = argparse.ArgumentParser(description='启动分布式服务的工具')

parser.add_argument('--service', type=str, default=False)

args = parser.parse_args()

startable_service_dict = {
    'blip': blip_img_cap.app.start,
    'chatglm3': llm.chatglm3.app.start,
    'asr': asr.app.start
}

if args.service:
    start_func = startable_service_dict.get(args.service)
    start_func()

import argparse

import blip_img_cap.service

parser = argparse.ArgumentParser(description='启动分布式服务的工具')

parser.add_argument('blip', type=bool, default=False)
# parser.add_argument('blip', type=bool, default=
# )

args = parser.parse_args()
if args.blip:
    blip_img_cap.service.start()
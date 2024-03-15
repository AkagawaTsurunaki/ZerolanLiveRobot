import argparse

from chatglm3 import service as llm_serv
from initzr import load_chatglm3_service_config, load_global_config

DEFAULT_GLOBAL_CONFIG_PATH = R'config/global_config.yaml'
g_config = load_global_config(DEFAULT_GLOBAL_CONFIG_PATH)


def start_llm():
    config = load_chatglm3_service_config(g_config)
    llm_serv.init(*config)
    llm_serv.start()


parser = argparse.ArgumentParser(description='Calculate volume of a cylinder')
parser.add_argument('--chatglm3', action='store_true', help='启动 ChatGLM3 服务')

args = parser.parse_args()


start_llm()

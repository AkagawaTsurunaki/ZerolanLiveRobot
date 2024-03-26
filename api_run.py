from chatglm3 import service as llm_serv
from initzr import load_chatglm3_service_config, load_global_config


def start_llm():
    g_config = load_global_config()
    config = load_chatglm3_service_config(g_config)
    llm_serv.init(*config)
    llm_serv.start()


start_llm()

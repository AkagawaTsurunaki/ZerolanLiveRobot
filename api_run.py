from chatglm3 import service as llm_serv
from chatglm3 import api as llm_api
from initzr import load_chatglm3_service_config, load_global_config

service = {
    'chatglm3': llm_serv
}
DEFAULT_GLOBAL_CONFIG_PATH = R'config/global_config.yaml'
g_config = load_global_config(DEFAULT_GLOBAL_CONFIG_PATH)



from common.utils.file_util import read_yaml, spath


def get_config():
    cfg_dict = read_yaml(spath("resources/config.yaml"))
    return cfg_dict
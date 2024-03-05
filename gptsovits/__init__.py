import os

from loguru import logger

import gptsovits.config as g_conf

try:
    if not os.path.exists(g_conf.tmp_dir):
        os.mkdir(g_conf.tmp_dir)
        logger.info(f'临时目录创建成功：{g_conf.tmp_dir}')
except Exception as e:
    g_conf.tmp_dir = r'gptsovits\.tmp'
    logger.warning(f'配置文件指定的临时目录无法被创建，使用默认临时目录')
    logger.warning(f'注意：临时目录如果选择相对路径，有一定概率无法播放音频')

# 临时目录
TMP_DIR = g_conf.tmp_dir

# 检查URL
SERVER_URL = f"{g_conf.host}:{g_conf.port}"

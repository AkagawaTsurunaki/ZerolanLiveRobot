import random
from typing import List

from bilibili_api import Credential, sync
from bilibili_api import Danmaku
from bilibili_api.live import LiveDanmaku, LiveRoom
from loguru import logger

import utils.util
from utils.datacls import Danmaku

# 该服务是否已被初始化?
g_is_service_inited = False

# 该服务是否正在运行?
g_is_service_running = False

# 弹幕队列
g_danmaku_list: List[Danmaku] = []

# 直播监视器（监控弹幕）
MONITOR: LiveDanmaku

# 直播发送器（发送弹幕）
SENDER: LiveRoom


def init(sessdata: str, bili_jct: str, buvid3: str, room_id: int):
    logger.info('🍻 Bilibili 直播服务正在初始化……')

    global MONITOR, SENDER, g_is_service_inited
    # 身份对象
    credential = Credential(sessdata=sessdata, bili_jct=bili_jct, buvid3=buvid3)
    # 监听直播间弹幕
    MONITOR = LiveDanmaku(room_id, credential=credential)
    # 用来发送弹幕
    SENDER = LiveRoom(room_id, credential=credential)
    assert MONITOR and SENDER, '❌️ Bilibili 直播服务初始化失败'
    g_is_service_inited = True

    logger.info('🍻 Bilibili 直播服务初始化完毕')

    @MONITOR.on("DANMU_MSG")
    async def recv(event):
        danmaku = Danmaku(uid=event["data"]["info"][2][0],
                          username=event["data"]["info"][2][1],
                          msg=event["data"]["info"][1],
                          ts=event["data"]["info"][9]['ts'],
                          is_read=False)
        # 注意没带粉丝牌的会导致越界
        # fans_band_level = event["data"]["info"][3][0]  # 粉丝牌的级别
        # fans_band_name = event["data"]["info"][3][1]  # 该粉丝牌的名字
        # live_host_name = event["data"]["info"][3][2]  # 该粉丝牌对应的主播名字

        logger.debug(f'🍥 [{danmaku.username}]({danmaku.uid}): {danmaku.msg}')

        _add(danmaku)

    return g_is_service_inited


# 启动监听
def start():
    global g_is_service_running
    g_is_service_running = True
    logger.info('🍻 Bilibili 直播间监听启动')
    sync(MONITOR.connect())
    logger.warning('🍻 Bilibili 直播间监听已结束')


def select_latest_longest(k: int) -> Danmaku:
    # 按照某种策略拾取弹幕
    # 按照当前时间戳最近的k条中随机挑选msg字段字符串最长的一条（若都相同，则随机）

    # 选择出未读过的弹幕
    unread_danmaku_list = [danmaku for danmaku in g_danmaku_list if not danmaku.is_read]

    # 如果弹幕数小于k
    if len(unread_danmaku_list) < k:
        selected_danmaku = max(unread_danmaku_list, key=lambda danmaku: len(danmaku.msg), default=None)
    # 如果弹幕数大于k
    else:
        recent_danmakus = sorted(unread_danmaku_list, key=lambda danmaku: danmaku.ts, reverse=True)[:k]
        max_length = max(len(danmaku.msg) for danmaku in recent_danmakus)
        longest_danmakus = [danmaku for danmaku in recent_danmakus if len(danmaku.msg) == max_length]
        selected_danmaku = random.choice(longest_danmakus) if longest_danmakus else None
    # 将选择的弹幕标记为已读
    if selected_danmaku:
        selected_danmaku.is_read = True
    return selected_danmaku


def _add(danmaku: Danmaku):
    # TODO: 这里可以实现多个过滤规则的运作
    g_danmaku_list.append(danmaku)
    logger.debug(f'添加 1 条弹幕于弹幕列表中，现在{len(g_danmaku_list)}')


def stop():
    """
    终止本服务
    :return:
    """
    global SENDER, g_is_service_running
    # 关闭监视器
    MONITOR.disconnect()
    # 删除发送器
    SENDER = None
    # 保存弹幕信息
    utils.util.save_service('bilibili', g_danmaku_list)
    # 设置 FLAG
    g_is_service_running = False
    return g_is_service_running

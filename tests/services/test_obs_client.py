import threading
import time

from common.config import get_config
from common.killable_thread import KillableThread
from services.obs.client import ObsStudioWsClient

s = """哈基米像一颗巨石按在胸口
哈基米阿西噶嗨呀库纳鲁多米吉哈
哦马吉里哈基米喔纳梅鲁多阿西噶
叮鸡咚鸡叮咚叮鸡zakozako onina
恐龙抗狼一段一段下来出示健康码
哈基米阿西噶嗨呀库纳鲁多米吉哈
哦马吉里哈基米喔纳梅鲁多阿西噶
叮鸡咚鸡叮咚叮鸡zakozako onina
恐龙抗狼一段一段下来出示健康码
阿西噶喔纳美噜多几点起床妈妈酱
曼波哈基好胖可爱楼上下去草哈基
离原上咪一岁一咪打野来搞小啾啾
野火哈咪春风吹咪小白手套ccb！
哈基米阿西噶嗨呀库纳鲁多米吉哈
哦马吉里哈基米喔纳梅鲁多阿西噶
叮鸡咚鸡叮咚叮鸡zakozako onina
哎哟我滴妈！
"""
_config = get_config()

_client = ObsStudioWsClient(_config.service.obs)


def test_conn():
    client_thread = KillableThread(target=_client.start, daemon=True)
    client_thread.start()
    time.sleep(1)
    if _client.is_connected:
        _client.subtitle(s, "assistant", 3)

    time.sleep(4)
    assert _client.is_connected, "Test failed!"
    threading.Thread(target=_client.stop, daemon=True).start()

    client_thread.kill()

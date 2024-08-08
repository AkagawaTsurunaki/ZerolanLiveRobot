import time

from services.live_stream.bilibili.service import BilibiliService
from loguru import logger

serv = BilibiliService()

serv.start()

logger.info("TTTTTTTTTTTTTTTT")
i = 0
while True:
    print(i)
    i += 1
    time.sleep(10)
    dbo = serv.danmaku_buf.select_latest_longest(k=2)
    if dbo is not None:
        danmaku = dbo.danmaku
        logger.debug(f"选择了 {danmaku}")

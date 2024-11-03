import asyncio

from loguru import logger

import init
from zerolan_live_robot_ui.api.toasts import Toast
from lifecycle.controller import Controller

virtual_character_name = "AkagawaTsurunaki"


async def run():
    init.start_ui_process()
    Toast(message="ZerolanLiveRobot UI 模块初始化完毕").show_toast()

    controller = Controller()
    await controller.awake()
    while True:
        try:
            await controller.update()
        except KeyboardInterrupt:
            logger.info(f"{virtual_character_name} 受键盘控制退出运行")
            exit()
        except Exception as e:
            logger.exception(e)

        await asyncio.sleep(2)


if __name__ == '__main__':
    asyncio.run(run(), debug=True)
    # enable debug mode on the current event loop
    loop = asyncio.get_running_loop()
    loop.set_debug(True)

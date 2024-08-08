import time

from manager.controller.minecraft_controller import MinecraftController

# with ProgressToast(message="即将控制...", busy=False) as bar:
time.sleep(4)
for i in range(3):
    time.sleep(1)
    # bar.set_message(message=f"控制等待 {i + 1}/3 秒", cur_value=i + 1)

controller = MinecraftController()
controller.start()

time.sleep(3)

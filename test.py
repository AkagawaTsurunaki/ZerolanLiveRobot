import time
from functools import wraps

from loguru import logger

import img_cap
import scrnshot.api
import vad.service
from karada.pipeline import FusionPipeline

p = FusionPipeline()

run_time_records: dict[str: list] = {
    scrnshot.__name__: [],
    img_cap.__name__: []
}


def calculate_average(records: dict[str, list]) -> dict[str, float]:
    averages = {}
    for key, values in records.items():
        if values:
            average_value = sum(values) / len(values)
            averages[key] = average_value
        else:
            averages[key] = 0  # 如果列表为空，则平均值为0
    return averages


def test_run_time(service_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                time_start = time.time()
                func(*args, **kwargs)
                time_end = time.time()
                time_used = "{:.2f}".format(time_end - time_start)
                logger.info(f"{service_name} 测试通过，用时：{time_used} 秒。")
                run_time_records[service_name].append(time_end - time_start)
                return True
            except Exception as e:
                logger.exception(e)
                logger.critical(f"{service_name} 测试失败，因为：{e}")
                return False

        return wrapper

    return decorator


@test_run_time(service_name=scrnshot.__name__)
def test_scrnshot():
    # 在作者 4080 Laptop 本机上，平均用时为0.05秒（仅供参考）。
    img = scrnshot.api.screen_cap()
    assert img


@test_run_time(service_name=img_cap.__name__)
def test_img_cap():
    # 在作者 4080 Laptop 本机上，平均用时为0.74秒（仅供参考）。
    caption = p.see()
    assert caption
    logger.debug(caption)


def run_test():
    # for _ in range(100):
    #     is_scrn_shot_passed = test_scrnshot()
    #     if is_scrn_shot_passed:
    #         test_img_cap()
    #
    # averages = calculate_average(run_time_records)
    # print(averages)
    vad.service.init()
    vad.service.start()


run_test()

import time

from loguru import logger
from selenium.webdriver import Keys
from selenium.webdriver.common.actions.action_builder import ActionBuilder

from services.device.screen import Screen
from zerolan.data.data.ocr import OCRQuery
from pipeline.ocr import OcrPipeline
from services.browser.driver import DriverInitializer

# 创建Chrome WebDriver实例
driver = DriverInitializer("firefox").get_driver()

# 打开指定的URL
url = 'https://cn.bing.com/'
driver.get(url)

# 假设搜索框的位置坐标已知（示例）
search_box_x = 750
search_box_y = 400

# 使用ActionChains控制鼠标移动到指定位置（插值缓慢移动）
action_builder = ActionBuilder(driver)
action_builder.pointer_action.move_to_location(x=search_box_x, y=search_box_y)

# 在搜索框中输入指定字符（示例）
search_text = 'Python Selenium'
action_builder.key_action.send_keys(search_text)
action_builder.key_action.key_down(Keys.ENTER)

action_builder.perform()

ActionBuilder(driver).clear_actions()

time.sleep(8)

img, img_path = Screen.capture("Firefox")
pipeline = OcrPipeline()

prediction = pipeline.predict(OCRQuery(img_path))

logger.info(prediction)
logger.info(prediction.unfold_as_str())

time.sleep(5)

# 关闭浏览器
# driver.quit()

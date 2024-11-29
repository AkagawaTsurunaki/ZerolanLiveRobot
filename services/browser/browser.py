from selenium.webdriver import Firefox, Chrome, Keys
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By

from common.config import BrowserConfig
from services.browser import driver
from services.browser.driver import DriverInitializer


class Browser:
    def __init__(self, config: BrowserConfig):
        self.driver: Firefox | Chrome = DriverInitializer(config).get_driver()

    def open(self, url: str):
        self.driver.get(url)

    def close(self):
        self.driver.close()

    def page_source(self):
        return self.driver.page_source

    def move_to_search_box(self):
        # Assuming the location coordinates of the search box are known (example)
        search_box_x = 750
        search_box_y = 400
        # Use ActionChains to control mouse movement to a specified position (interpolation moves slowly)
        action_builder = ActionBuilder(driver)
        action_builder.pointer_action.move_to_location(x=search_box_x, y=search_box_y)

    # Enter a specified character in the search box (example)
    def send_keys_and_enter(self, keys):
        action_builder = ActionBuilder(self.driver)
        action_builder.key_action.send_keys(keys)
        action_builder.key_action.key_down(Keys.SPACE)
        action_builder.key_action.key_down(Keys.ENTER)
        action_builder.perform()

    def search(self, text: str):
        sb_form = self.driver.find_element(By.ID, 'sb_form_q')
        sb_form.send_keys(text)

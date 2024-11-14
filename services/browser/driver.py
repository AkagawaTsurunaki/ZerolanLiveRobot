import getpass
import os

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FireFoxWebDriver

from common.config import BrowserConfig
from common.utils import file_util


class DriverInitializer:

    def __init__(self, config: BrowserConfig) -> None:
        self._browser = config.driver
        self._profile_dir = config.profile_dir
        self._driver = None

    def find_firefox_profile_dir(self):

        if self._profile_dir is None or os.path.exists(self._profile_dir):
            # Auto search if not set in the config
            logger.info("Searching for FireFox Profiles...")
            username = getpass.getuser()
            logger.debug(f"Current user: {username}")
            if os.name == 'nt':
                default_profile_dir = f"C:/Users/{username}/AppData/Roaming/Mozilla/Firefox/Profiles"
                self._profile_dir = file_util.find_dir(default_profile_dir, ".default-release")

            if self._profile_dir is None:
                raise Exception("Can not find FireFox Profiles. Please set it in your config manually.")
            else:
                logger.info(f"Probable FireFox Profiles directory: {self._profile_dir}")

    def load_firefox_driver(self):
        profile = webdriver.FirefoxProfile(self._profile_dir)
        options = webdriver.FirefoxOptions()
        options.profile = profile
        driver = webdriver.Firefox(options=options)

        logger.info("Firefox Driver 加载完毕")
        self._driver = driver

    def get_driver(self) -> FireFoxWebDriver | ChromeWebDriver:
        if self._browser == "chrome":
            raise NotImplementedError()
        elif self._browser == "firefox":
            self.load_firefox_driver()

        return self._driver

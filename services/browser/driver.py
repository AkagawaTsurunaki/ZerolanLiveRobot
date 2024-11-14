import getpass
import os
from typing import Literal

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FireFoxWebDriver


from common.utils import file_util


class DriverInitializer:

    def __init__(self, browser: Literal["chrome", "firefox"]) -> None:
        self._browser = browser
        self._driver = None

    @staticmethod
    def get_firefox_profile_dir() -> str:

        # 从配置文件中读取
        profile_dir: str | None = AutoConfigLoader.config.get("Tasks.Browser.Selenium.Firefox.ProfileDir", None)

        if profile_dir is None or os.path.exists(profile_dir):
            # 配置文件中找不到自动获取
            logger.info("正在自动寻找 FireFox Profiles 目录")
            username = getpass.getuser()
            logger.debug(f"当前系统用户：{username}")
            default_profile_dir = f"C:/Users/{username}/AppData/Roaming/Mozilla/Firefox/Profiles"
            profile_dir = file_util.find_dir(default_profile_dir, ".default-release")
            assert profile_dir is not None, f"找不到 FireFox Profiles 目录，请检查后重试。"

        logger.info(f"找到可能的 FireFox Profiles 目录: {profile_dir}")
        return profile_dir

    def load_firefox_driver(self):
        profile_dir: str = DriverInitializer.get_firefox_profile_dir()
        profile = webdriver.FirefoxProfile(profile_dir)
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

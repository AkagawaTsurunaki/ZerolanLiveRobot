from utils.util import read_yaml


class Config:
    def __init__(self):
        self.config: dict = read_yaml("./config/config.yaml")

    def llm(self):
        config = self.config.get('llm')

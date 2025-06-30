import yaml

from common.generator.config_gen import ConfigFileGenerator
from config import ZerolanLiveRobotConfig


def read_yaml(path: str):
    with open(path, mode="r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_gen():
    g = ConfigFileGenerator()
    s = g.generate_yaml(ZerolanLiveRobotConfig())
    print(s)
    path = r"D:\AkagawaTsurunaki\WorkSpace\PythonProjects\ZerolanLiveRobot\resources\t.yaml"
    with open(path, mode="w+",
              encoding="utf-8") as f:
        f.write(s)
    d = read_yaml(path)
    print(d)

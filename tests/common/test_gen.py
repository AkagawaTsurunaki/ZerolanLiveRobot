from common.config import ZerolanLiveRobotConfig
from common.gen import ConfigFileGenerator
from common.utils.file_util import read_yaml


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
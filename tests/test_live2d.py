from common.config import get_config
from services.live2d.app import Live2dApplication

_config = get_config()


def test_live2d():
    serv = Live2dApplication(_config.service.live2d)
    serv.start()


test_live2d()
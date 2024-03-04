import dataclasses
from enum import Enum
import psutil


class Code(Enum):
    # 成功
    OK = 0
    # 端口已被占用
    PORT_IS_ALREADY_USED = 100
    # 路径不存在
    PATH_DOSE_NOT_EXIST = 101
    # 错误
    ERROR = 500


@dataclasses
class HttpResponseBody:
    code: int = Code.OK
    msg: str = ""
    data = None


def is_port_in_use(port):
    for proc in psutil.process_iter():
        for con in proc.connections():
            if con.status == 'LISTEN' and con.laddr.port == port:
                return True
    return False

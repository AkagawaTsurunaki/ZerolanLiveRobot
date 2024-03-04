from dataclasses import dataclass
from enum import Enum
import psutil


class Code(Enum):
    OK = 0
    PORT_IS_ALREADY_USED = 100
    PATH_DOSE_NOT_EXIST = 101
    ERROR = 500


@dataclass
class HttpResponseBody:
    code: Code = Code.OK
    msg: str = ""
    data = None


def is_port_in_use(port):
    for proc in psutil.process_iter():
        for con in proc.connections():
            if con.status == 'LISTEN' and con.laddr.port == port:
                return True
    return False

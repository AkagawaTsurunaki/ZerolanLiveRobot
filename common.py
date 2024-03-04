import json
from dataclasses import dataclass
from enum import Enum
import psutil

import chatglm3.common


class Code(Enum):
    OK = 0
    PORT_IS_ALREADY_USED = 100
    PATH_DOSE_NOT_EXIST = 101
    ERROR = 500


@dataclass
class HttpResponseBody:
    code: int
    msg: str
    data: chatglm3.common.ModelResponse | chatglm3.common.ModelRequest = None


class CodeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return json.JSONEncoder.default(self, obj)


def is_port_in_use(port):
    for proc in psutil.process_iter():
        for con in proc.connections():
            if con.status == 'LISTEN' and con.laddr.port == port:
                return True
    return False

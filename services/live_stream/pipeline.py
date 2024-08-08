from dataclasses import dataclass


@dataclass
class Danmaku:
    uid: str  # 弹幕发送者UID
    username: str  # 弹幕发送者名称
    msg: str  # 弹幕发送内容
    ts: int  # 弹幕时间戳

    def __str__(self):
        return f'[{self.username}]({self.uid}): {self.msg}'

from dataclasses import dataclass


@dataclass
class Config:
    # 是否以调试模式运行
    debug: bool
    # gptsovits 服务的主机地址
    host: str
    # gptsovits 服务的端口号
    port: int
    # gptsovits 模型生成临时语音文件的位置
    tmp_dir: str


@dataclass
class Request:
    text: str
    text_language: str

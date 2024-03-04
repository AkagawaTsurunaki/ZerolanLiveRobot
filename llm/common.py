from dataclasses import dataclass
from typing import List


@dataclass
class Config:
    # 是否以调试模式运行
    debug: bool
    # LLM 服务的主机地址
    host: str
    # LLM 服务的端口号
    port: int
    # Tokenizer 的路径
    tokenizer_path: str
    # 大预言模型的路径（请注意 Tokenizer 和模型不是一个概念）
    model_path: str
    # 量化等级
    quantize: int


@dataclass
class Request:
    sys_prompt: str
    query: str
    history: List[str]

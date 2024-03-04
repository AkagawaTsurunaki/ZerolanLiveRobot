import dataclasses
from typing import List

@dataclasses
class Config:
    # LLM 服务的主机地址
    host: str = "127.0.0.1"
    # LLM 服务的端口号
    port: int = 8721
    # Tokenizer 的路径
    tokenizer_path = "/"
    # 大预言模型的路径（请注意 Tokenizer 和模型不是一个概念）
    model_path = "/"

@dataclasses
class Request:
    sys_prompt: str = ""
    query: str = ""
    history: List[str] = []

import sys

import yaml
from pydantic import BaseModel
from zerolan.ump.pipeline.asr import ASRPipelineConfig
from zerolan.ump.pipeline.img_cap import ImgCapPipelineConfig
from zerolan.ump.pipeline.llm import LLMPipelineConfig
from zerolan.ump.pipeline.ocr import OCRPipelineConfig
from zerolan.ump.pipeline.tts import TTSPipelineConfig
from zerolan.ump.pipeline.vid_cap import VidCapPipelineConfig
from zerolan.ump.pipeline.vla import ShowUIConfig

from common.config import VectorDBConfig, VLAPipelineConfig, PipelineConfig, ZerolanLiveRobotConfig, ServiceConfig, \
    CharacterConfig, ExternalToolConfig, ResourceServerConfig, LiveStreamConfig, GameBridgeConfig, \
    PlaygroundBridgeConfig, QQBotBridgeConfig, BilibiliServiceConfig, TwitchServiceConfig, YoutubeServiceConfig, \
    ChatConfig, SpeechConfig, FilterConfig
from services.obs.config import ObsStudioClientConfig


def gen_pipeline_config():
    asr = ASRPipelineConfig(
        model_id="",
        predict_url="http://127.0.0.1:11000/asr/predict",
        stream_predict_url="http://127.0.0.1:11000/asr/stream-predict",
    )
    llm = LLMPipelineConfig(
        model_id="",
        predict_url="http://127.0.0.1:11000/llm/predict",
        stream_predict_url="http://127.0.0.1:11000/llm/stream-predict",
    )
    img_cap = ImgCapPipelineConfig(
        model_id="",
        predict_url="http://127.0.0.1:11000/img_cap/predict",
        stream_predict_url="http://127.0.0.1:11000/img-cap/stream-predict",
    )
    ocr = OCRPipelineConfig(
        model_id="",
        predict_url="http://127.0.0.1:11000/ocr/predict",
        stream_predict_url="http://127.0.0.1:11000/ocr/stream-predict",
    )
    vid_cap = VidCapPipelineConfig(
        model_id="",
        predict_url="http://127.0.0.1:11000/vid_cap/predict",
        stream_predict_url="http://127.0.0.1:11000/vid-cap/stream-predict",
    )
    tts = TTSPipelineConfig(
        model_id="",
        predict_url="http://127.0.0.1:11000/tts/predict",
        stream_predict_url="http://127.0.0.1:11000/tts/stream-predict",
    )
    vla = VLAPipelineConfig(
        showui=ShowUIConfig(
            model_id="",
            predict_url="http://127.0.0.1:11000/vla/showui/predict",
            stream_predict_url="http://127.0.0.1:11000/vla/showui/stream-predict",
        )
    )
    vec_db = VectorDBConfig(
        insert_url="http://127.0.0.1:11000/milvus/insert",
        search_url="http://127.0.0.1:11000/milvus/search",
    )

    config = PipelineConfig(
        asr=asr,
        llm=llm,
        img_cap=img_cap,
        ocr=ocr,
        vid_cap=vid_cap,
        tts=tts,
        vla=vla,
        vec_db=vec_db)

    return config


def gen_service_config():
    config = ServiceConfig(
        res_server=ResourceServerConfig(),
        live_stream=LiveStreamConfig(
            bilibili=BilibiliServiceConfig(),
            twitch=TwitchServiceConfig(),
            youtube=YoutubeServiceConfig()
        ),
        game=GameBridgeConfig(),
        playground=PlaygroundBridgeConfig(),
        qqbot=QQBotBridgeConfig(),
        obs=ObsStudioClientConfig(),
    )
    return config


def gen_config():
    pipeline_config = gen_pipeline_config()
    config = ZerolanLiveRobotConfig(
        pipeline=pipeline_config,
        service=gen_service_config(),
        character=CharacterConfig(
            bot_name="赤川小喵(Koneko)",
            chat=ChatConfig(
                filter=FilterConfig(
                    bad_words=[
                        "作为一名人工智能助手",
                        "人工智能助手",
                        "作为一个人工智能",
                        "作为一个AI"
                    ]
                ),
                system_prompt='你现在是叫做“赤川小喵”的一名猫娘，你的开发者是赤川鹤鸣。\n我会为你提供语音识别、图像识别、图像理解、语音合成和一系列的 AI 集成功能。\n你现在正在直播平台上与观众友好交流，请把自己当成一名真正的人类，与观众友好交流。\n你的话不要太长，控制在50字左右。',
                injected_history=[
                    "你叫什么名字？",
                    "我是赤川小喵，很高兴见到你！",
                    "你是谁研发出来的？",
                    "我是由赤川鹤鸣（AkagawaTsurunaki）研发的。"
                ],
                max_history=20
            ),
            speech=SpeechConfig()
        ),
        external_tool=ExternalToolConfig()
    )
    return config


def dump(config: ZerolanLiveRobotConfig):
    yaml_str = yaml.dump(config.model_dump(), allow_unicode=True)
    print(yaml_str)


yaml_str = ""


def model_to_yaml_with_comments(model: BaseModel, indent: int = 0) -> str:
    global yaml_str
    """
    将 Pydantic 模型转换为带描述注释的 YAML 字符串。
    :param model: Pydantic 模型实例
    :param indent: 当前缩进级别（默认为 0）
    :return: 带描述注释的 YAML 字符串
    """
    # 获取模型的字段信息
    fields = model.model_fields

    # yaml_str = yaml.dump(model.model_dump(), allow_unicode=True)

    for field_name, field_info in fields.items():
        description = field_info.description or ""
        field_val = model.__getattribute__(field_name)
        if isinstance(field_val, BaseModel):
            # print(type(field_val))
            yaml_str += " " * indent + f"{field_name}:\n"
            model_to_yaml_with_comments(field_val, indent + indent)
        else:
            if field_info.description:
                yaml_str += " " * indent + f"# {field_info.description}\n"
            # kv = yaml.dump({field_name: field_val}, sys.stdout, allow_unicode=True)
            # yaml_str += " " * indent + f"{kv}\n"
            if isinstance(field_val, str):
                yaml_str += " " * indent + f"{field_name}: '{field_val}'\n"
            else:
                yaml_str += " " * indent + f"{field_name}: {field_val}\n"
            # yaml_str += yaml.dump(field_val, allow_unicode=True) + "\n"
        # print(field_name, description)
    return yaml_str



from controller import DEFAULT_EMOTION_OUTPUT_PATH, DEFAULT_LLM_OUTPUT_PATH
from emo import Emotion


def write_output(danmaku, text: str, emotion: Emotion):
    """
    将获取到的弹幕，LLM 输出的文本，和文本所蕴含的情感写入 OBS 字幕文件中。
    :param danmaku: 弹幕对象
    :param text: LLM 输出的文本字符串
    :param emotion: 情感对象
    """
    with open(file=DEFAULT_EMOTION_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
        file.write(emotion.id)
    with open(file=DEFAULT_LLM_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
        file.write(f'{text}')
    with open(file=DEFAULT_EMOTION_OUTPUT_PATH, mode='w+', encoding='utf-8') as file:
        if danmaku:
            file.write(f'{danmaku.username}: {danmaku.msg}')

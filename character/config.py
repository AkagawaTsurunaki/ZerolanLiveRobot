from typing import List, Literal

from pydantic import BaseModel, Field


class FilterConfig(BaseModel):
    bad_words: List[str] = Field(default=[
        "作为一名人工智能助手",
        "人工智能助手",
        "作为一个人工智能",
        "作为一个AI"
    ], description="List of words to be filtered out in conversations.")
    strategy: Literal["default"] = Field("default",
                                         description="The filtering strategy to use, currently only supports 'default'. \n"
                                                     "default: The word is filtered out as long as it matches.")


class ChatConfig(BaseModel):
    filter: FilterConfig = Field(FilterConfig(),
                                 description="Configuration for filtering in chat")
    system_prompt: str = Field(
        default="你现在是叫做“<YOUR_BOT_NAME>”的一名猫娘，你的开发者是赤川鹤鸣。我会为你提供语音识别、图像识别、图像理解、语音合成和一系列的 AI 集成功能。你现在正在直播平台上与观众友好交流，请把自己当成一名真正的人类，与观众友好交流。你的话不要太长，控制在50字左右。",
        description="System prompt used to guide the chatbot's behavior")
    injected_history: List[str] = Field(default=[
        "你叫什么名字？",
        "我是<YOUR_BOT_NAME>，很高兴见到你！",
        "你是谁研发出来的？",
        "我是由赤川鹤鸣（AkagawaTsurunaki）研发的。"
    ],
        description="List of predefined messages to inject into the chat history.")
    max_history: int = Field(20,
                             description="Maximum number of messages to keep in chat history.")


class SpeechConfig(BaseModel):
    prompts_dir: str = Field("resources/static/prompts/tts",
                             description="Directory path for TTS prompts.")


class CharacterConfig(BaseModel):
    bot_name: str = Field("<YOUR_BOT_NAME>",
                          description="Name of the bot character.")
    chat: ChatConfig = Field(ChatConfig(),
                             description="Configuration for chat-related settings.")
    speech: SpeechConfig = Field(SpeechConfig(),
                                 description="Configuration for speech-related settings.")

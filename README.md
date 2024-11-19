# ZerolanLiveRobot 2.0

![Static Badge](https://img.shields.io/badge/Python%20-%203.10%20-%20blue) ![Static Badge](https://img.shields.io/badge/Node%20-%2020.9.0%20-%20violet) ![Static Badge](https://img.shields.io/badge/CUDA%20-%202.1.1%2Bcu118%20-%20green) ![Static Badge](https://img.shields.io/badge/License%20-%20GPLv3%20-%20orange)

![Static Badge](https://img.shields.io/badge/AI%20VTuber%20-%20green) ![Static Badge](https://img.shields.io/badge/Bilibli%20Live%20-%20green) ![Static Badge](https://img.shields.io/badge/Large%20Language%20Model%20-%20green) ![Static Badge](https://img.shields.io/badge/Text%20to%20Speech%20-%20green) ![Static Badge](https://img.shields.io/badge/Image%20to%20Text%20-%20green) ![Static Badge](https://img.shields.io/badge/Minecraft%20AI%20Agent%20-%20green) ![Static Badge](https://img.shields.io/badge/Automatic%20Speech%20Recognition%20(coming%20soon)%20-%20blue)


你或许已经听说过著名的 [Neurosama](https://virtualyoutuber.fandom.com/wiki/Neuro-sama)
，或者是来自中国的[木几萌](https://mobile.moegirl.org.cn/%E6%9C%A8%E5%87%A0%E8%90%8C)。
你是否也想要拥有一个自己的 AI 虚拟形象陪你直播、聊天、打游戏？
开源的 Zerolan Live Robot 正致力于实现您的梦想！而这仅仅需要一张消费级显卡！

Zerolan Live Robot 是一款多功能的直播机器人（AI VTuber），它可以自动在 Bilibili 直播间中读取弹幕，观察电脑屏幕的指定窗口，理解其画面内容，操纵
Minecraft 中的游戏角色，做出带情感的语音聊天回应。

本项目集成了众多开源的、可本地部署的人工智能模型或服务，旨在使用通用的管线和统一的 Web API
接口封装大语言模型（LLM）、自动语音识别（ASR）、文本转语音（TTS）、图像字幕（Image
Captioning）、光学字符识别（OCR）等一系列的人工智能模型。并可以使用统一的配置文件和服务启动器快速部署和启动 AI 服务。

与其关联的项目 [KonekoMinecraftBot](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot)、[zerolan-core](https://github.com/AkagawaTsurunaki/zerolan-core)、[zerolan-data](https://github.com/AkagawaTsurunaki/zerolan-data)、[zerolan-ui](https://github.com/AkagawaTsurunaki/zerolan-ui)。

> [!Note]
>
> 本项目持续开发中，当前的版本为 `2.0`
> ，您可以关注开发者的Bilibili账号[赤川鹤鸣_Channel](https://space.bilibili.com/1076299680)，正在根据此项目调教 AI
> 猫娘，不定时直播展示最新进展。

| 支持项      | 支持内容                                                                                                                                                                                                                                                                                     |
|----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 直播平台     | [Bilibili](https://www.bilibili.com) \| [Twitch](https://www.twitch.tv)                                                                                                                                                                                                                |
| 大语言模型    | [GLM-4](https://github.com/THUDM/GLM-4) \| [chatglm3-6b](https://github.com/THUDM/ChatGLM3) \| [Qwen-7B-Chat](https://huggingface.co/Qwen/Qwen-7B-Chat) \| [Yi-6B-Chat](https://www.modelscope.cn/models/01ai/Yi-6B-Chat) \| [shisa-7b-v1](https://huggingface.co/augmxnt/shisa-7b-v1) 
| 自动语音识别模型 | [speech_paraformer_asr](https://www.modelscope.cn/models/iic/speech_paraformer_asr_nat-zh-cn-16k-common-vocab8358-tensorflow1)                                                                                                                                                         |
| 语音合成模型   | [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)                                                                                                                                                                                                                                   |
| 图像字幕模型   | [Salesforce/blip-image-captioning-large](https://huggingface.co/Salesforce/blip-image-captioning-large)                                                                                                                                                                                |
| 光学字符识别模型 | [PaddleOCR](https://gitee.com/paddlepaddle/PaddleOCR)                                                                                                                                                                                                                     |                                                                                                                                                                                                                                                                                       |

## 安装方式

> [!Warning]
>
> ZerolanLiveRobot 2.0 版本与旧版本不兼容，因此您可能需要重新配置环境、安装依赖。

运行指令，这会安装基础环境需要的依赖包。

```shell
conda create --name ZerolanLiveRobot python=3.10
conda activate ZerolanLiveRobot
pip install -r requirements.txt
```

在开发分支您需要额外安装的有

```shell
pip install git+https://github.com/AkagawaTsurunaki/zerolan-ui.git@dev
pip install git+https://github.com/AkagawaTsurunaki/zerolan-data.git@dev
```

注意，各个AI模型可能依赖了不同版本的依赖，为了防止冲突，请根据 `/services` 下各个模型文件夹中所带的 `requirements.txt`
文件按需下载。

## 集成模型

注意：以问号标注表示数据暂时未测量。

以下的模型已经过作者的测试，可以正常使用，然而不同系统的环境差异显著，实在无法广泛覆盖所有情况，如有意外敬请谅解。

### 大语言模型

根据自然语言上下文进行推理，并给予文字答复。

| 模型名称                                                                 | 支持语言 | 流式推理 | 显存占用                                                      |
|----------------------------------------------------------------------|------|------|-----------------------------------------------------------|
| [THUDM/chatglm3-6b](https://github.com/THUDM/ChatGLM3)               | 中英   | 支持   | 无量化 11.5 GiB <br> 8-Bit 量化 6.6  GiB <br> 4-Bit 量化 4.0 GiB |
| [Qwen/Qwen-7B-Chat](https://huggingface.co/Qwen/Qwen-7B-Chat)        | 中英   | 支持   | 11.5 GiB                                                  |
| [01-ai/Yi-6B-Chat](https://www.modelscope.cn/models/01ai/Yi-6B-Chat) | 中英   | 不支持  | 10.0 GiB                                                  |
| [augmxnt/shisa-7b-v1](https://huggingface.co/augmxnt/shisa-7b-v1)    | 日英   | 不支持  | 11.4 GiB                                                  |

注意：

1. [THUDM/chatglm3-6b](https://github.com/THUDM/ChatGLM3) 也支持简单的日语或其他语言，但效果欠佳。
2. [Qwen/Qwen-7B-Chat](https://huggingface.co/Qwen/Qwen-7B-Chat) 测试时发现使用多卡推理可能会报错，因此您应该使用单卡推理。
3. [01-ai/Yi-6B-Chat](https://www.modelscope.cn/models/01ai/Yi-6B-Chat) 与本项目环境冲突，需要额外配置 Python
   虚拟环境，详见 `src/services/llm/yi/requirements.txt`。
4. [augmxnt/shisa-7b-v1](https://huggingface.co/augmxnt/shisa-7b-v1) 支持日语，但不支持流式推理。

### 自动语音识别模型

识别一段语音，将其转换为文本字符串的模型。

| 模型名称                                                                                                                                                                          | 支持语言 | 显存占用    |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------|---------|
| [iic/speech_paraformer_asr_nat-zh-cn-16k-common-vocab8358-tensorflow1](https://www.modelscope.cn/models/iic/speech_paraformer_asr_nat-zh-cn-16k-common-vocab8358-tensorflow1) | 中英   | 0.5 GiB |

### 文本转语音模型

根据给定的参考音频和文本，生成对应的语音。

| 模型名称                                                          | 支持语言  | 显存占用    |
|---------------------------------------------------------------|-------|---------|
| [RVC-Boss/GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) | 中粤日英韩 | 1.3 GiB |

[GPT-SoVITS](https://github.com/AkagawaTsurunaki/GPT-SoVITS) 的安装教程请参考官方 `README.md`，请注意必须是
[AkagawaTsurunaki](https://github.com/AkagawaTsurunaki) 的 Forked 版本才能与本项目的接口适配。

### 图像字幕模型

识别一张图片，生成对这张图片内容的文字描述。

| 模型名称                                                                                                    | 支持语言 | 显存占用 |
|---------------------------------------------------------------------------------------------------------|------|------|
| [Salesforce/blip-image-captioning-large](https://huggingface.co/Salesforce/blip-image-captioning-large) | 英文   | -    |

注意：[Salesforce/blip-image-captioning-large](https://huggingface.co/Salesforce/blip-image-captioning-large)
存在一定的幻觉问题，即容易生成与图片中内容无关的内容。本人在像素沙盒游戏 Minecraft 中测试，该模型生成的内容幻觉现象尤为严重。

### 光学字符识别模型

识别一张图片，并将其中包含的文字字符提取出。

| 模型名称                                                               | 支持语言   | 显存占用    |
|--------------------------------------------------------------------|--------|---------|
| [paddlepaddle/PaddleOCR](https://gitee.com/paddlepaddle/PaddleOCR) | 中英法德韩日 | 0.2 GiB |

PaddleOCR 会自动下载，因此配置文件中的路径可以不进行指定。

### 语音激活检测

识别当前环境中是否有人在说话。

> 目前仅基于音频能量的对环境音频进行了简单的检测。

## API 文档

> 正在开发中……待补充

## 常见问题

### 模型服务启动失败

启动后日志显示“在其上下文中，该请求的地址无效。”。

解决方案，检查配置文件中，`host` 的配置是否正确。如果想要本机开启，请指定为 `'127.0.0.1'`。

## Contact with Me

**Email**: AkagawaTsurunaki@outlook.com

**Github**: AkagawaTsurunaki
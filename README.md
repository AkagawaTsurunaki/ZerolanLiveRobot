# Zerolan Live Robot 2.0

![Static Badge](https://img.shields.io/badge/Python%20-%203.10%20-%20blue) ![Static Badge](https://img.shields.io/badge/License-MIT-orange) ![Static Badge](https://img.shields.io/badge/AI%20VTuber-blue) ![Static Badge](https://img.shields.io/badge/Bilibli-fb7299) ![Static Badge](https://img.shields.io/badge/Youtube-ff0000) ![Static Badge](https://img.shields.io/badge/Twitch-9044fe) ![Static Badge](https://img.shields.io/badge/ASR-purple) ![Static Badge](https://img.shields.io/badge/LLM-purple) ![Static Badge](https://img.shields.io/badge/TTS-purple) ![Static Badge](https://img.shields.io/badge/OCR-purple) ![Static Badge](https://img.shields.io/badge/ImageCaptioning-purple) ![Static Badge](https://img.shields.io/badge/VideoCaptioning-purple) ![Static Badge](https://img.shields.io/badge/MinecraftAIAgent-purple) ![Static Badge](https://img.shields.io/badge/ver-2.0-green)

你或许已经听说过著名的 [Neurosama](https://virtualyoutuber.fandom.com/wiki/Neuro-sama)，或者是来自中国的[木几萌](https://mobile.moegirl.org.cn/%E6%9C%A8%E5%87%A0%E8%90%8C)。你是否也想要拥有一个自己的 AI 虚拟形象陪你直播、聊天、打游戏？开源的 Zerolan Live Robot 正致力于实现您的梦想！而这仅仅需要一张消费级显卡！

Zerolan Live Robot 是一款多功能的直播机器人（AI VTuber），它可以自动在 Bilibili 直播间中读取弹幕，观察电脑屏幕的指定窗口，理解其画面内容，操纵
Minecraft 中的游戏角色，做出带情感的语音聊天回应。

与其关联的项目 [KonekoMinecraftBot](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot)、[zerolan-core](https://github.com/AkagawaTsurunaki/zerolan-core)、[zerolan-data](https://github.com/AkagawaTsurunaki/zerolan-data)、[zerolan-ui](https://github.com/AkagawaTsurunaki/zerolan-ui)。

> [!Note]
>
> 本项目持续开发中，当前的版本为 `2.0`，您可以关注开发者的 Bilibili 账号[赤川鹤鸣_Channel](https://space.bilibili.com/1076299680)，正在根据此项目调教 AI 猫娘，不定时直播展示最新进展。

## 特点与功能

- [x] 💭 基于大语言模型的自然语言对话
- [x] 🍻 根据直播间弹幕挑选并回复
- [x] 🎙️ 识别用户麦克风语音输入内容，理解并回复
- [x] 📣 根据回复文本的带情感的语音合成
- [x] 📄 识别指定窗口中的文字内容
- [x] 🖼️ 识别指定窗口中的图像（或视频），并理解其中的含义
- [x] 🛠️ 根据上下文语境采取行动或挑选工具（百度百科、萌娘百科等）
- [x] 🕹 根据语音指令控制 Minecraft AI 智能体
- [ ] Live2D 形象的控制
- [ ] 智能体的记忆功能

以下简要列出了本项目支持的内容：


| 支持项           | 支持内容                                                     |
| ---------------- | ------------------------------------------------------------ |
| 直播平台         | [Bilibili](https://www.bilibili.com) \| [Twitch](https://www.twitch.tv) |
| 大语言模型       | [THUDM/GLM-4](https://github.com/THUDM/GLM-4) \| [THUDM/ChatGLM3](https://github.com/THUDM/ChatGLM3) \| [Qwen/Qwen-7B-Chat](https://huggingface.co/Qwen/Qwen-7B-Chat) \| [01ai/Yi-6B-Chat](https://www.modelscope.cn/models/01ai/Yi-6B-Chat) \| [augmxnt/shisa-7b-v1](https://huggingface.co/augmxnt/shisa-7b-v1) |
| 自动语音识别模型 | [iic/speech_paraformer_asr](https://www.modelscope.cn/models/iic/speech_paraformer_asr_nat-zh-cn-16k-common-vocab8358-tensorflow1) |
| 语音合成模型     | [RVC-Boss/GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) |
| 图像字幕模型     | [Salesforce/blip-image-captioning-large](https://huggingface.co/Salesforce/blip-image-captioning-large) |
| 光学字符识别模型 | [paddlepaddle/PaddleOCR](https://gitee.com/paddlepaddle/PaddleOCR) |
| 视频字幕模型     | [iic/multi-modal_hitea_video-captioning_base_en](https://www.modelscope.cn/models/iic/multi-modal_hitea_video-captioning_base_en) |
| 外部可调用工具   | 火狐浏览器、百度百科、萌娘百科                               |
| 游戏插件         | Minecraft                                                    |

## 安装并运行

> [!CAUTION]
>
> Zerolan Live Robot 2.0 版本与旧版本 1.0 不兼容，因此您可能需要重新配置环境、安装依赖。

Zerolan 框架由 Zerolan Live Robot、Zerolan Core、Zerolan Data、Zerolan UI 共同组成。下表简要地介绍了各个项目的用途：

| 项目名                                                       | 用途                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [Zerolan Live Robot](https://github.com/AkagawaTsurunaki/ZerolanLiveRobot) | 直播机器人的控制框架，通过采集环境数据，并综合分析做出动作响应。 |
| [Zerolan Core](https://github.com/AkagawaTsurunaki/zerolan-core) | 为直播机器人提供 AI 推理服务的核心模块，例如大语言模型的 Web API 服务化。 |
| [Zerolan Data](https://github.com/AkagawaTsurunaki/zerolan-data) | 定义各个服务之间利用网络请求交换的数据格式。                 |
| [Zerolan UI](https://github.com/AkagawaTsurunaki/zerolan-ui) | 基于 PyQT6 的 GUI 界面，包括顶部弹窗和提示音等。             |

### 部署核心服务

> [!IMPORTANT]
>
> 此步骤是**必须**的！

请移步至[此处](https://github.com/AkagawaTsurunaki/zerolan-core)进完成 Zerolan Core 的相关部署工作，Zerolan Live Robot 强依赖于此核心服务。

### 安装本项目依赖

运行指令，这会创建一个虚拟环境并激活，然后自动安装本项目需要的依赖包：

```shell
conda create --name ZerolanLiveRobot python=3.10
conda activate ZerolanLiveRobot
pip install -r requirements.txt
```

如果您在 `dev` 开发分支，您可能需要手动安装：

```shell
pip install git+https://github.com/AkagawaTsurunaki/zerolan-ui.git@dev
pip install git+https://github.com/AkagawaTsurunaki/zerolan-data.git@dev
```

### 修改配置

找到 `resources/config.template.yaml` 配置文件，更名为 `config.yaml` ，然后根据配置文件中的注释修改为您需要的配置。

#### Pipeline

`pipeline` 配置项中，您需要注意的是，`server_url` 应该包含协议、IP以及端口号，例如 `http://127.0.0.1:11001`、`https://myserver.com:11451` 等，这是您部署 Zerolan Core 的网络地址，每一类模型可能有不同的端口。

> [!TIP]
> 
> 服务器只能开启一个端口？那么请尝试使用 Nginx 转发你的请求。

#### Service

`service` 配置项中，您需要注意的是，`host` 应仅包含 IP 地址，`port` 应仅包含端口号。

`game.platform` 字段支持的有 `minecraft`，`live_stream` 字段支持的有 `bilibili`、`twitch`、`youtube`。

> [!TIP]
> 
> 获取直播平台 API Key 可能使用到的文档：
> 
> Bilibili：[获取 Credential 类所需信息](https://nemo2011.github.io/bilibili-api/#/get-credential?id=获取-credential-类所需信息)
> 
> Twitch：[Twitch Developers - Authentication](https://dev.twitch.tv/docs/authentication/)
> 
> Youtube：[Obtaining authorization credentials](https://developers.google.cn/youtube/registering_an_application?hl=en)

#### Character

`character.chat.filter.strategy` 的值可以为 `default`。

`character.chat.filter.bad_words` 可以填写一系列的过滤词。

`character.chat.injected_history` 这个数组必须为偶数个，即必须为 AI 回复的消息结尾。

`character.chat.max_history` 指明了最多保留多少条消息，即消息窗口的大小。

`character.speech.prompts_dir` 指明了你的 TTS 音频文件的存放位置，你的文件名的格式应为 `[语言][情感标签]文本内容.wav`。例如`[zh][开心]哇！今天真是一个好天气.wav`，其中“语言”仅支持`zh`、`en`、`ja`；“情感标签”任意，只要能让大语言模型判别即可；“文本内容”为这段音频中人声所代表的文本内容。

#### External Tool

> [!CAUTION]
>
> Microsoft Edge 浏览器可能存在内存泄露，因此此项目不支持。

`external_tool.browser.driver` 可选的值有 `firefox`。

`external_tool.browser.profile_dir` 是为了保证在 Selenium 的控制下，您的账号登录等信息不会丢失，留空程序会自动检测位置（但不代表一定能找到）。

### 启动本项目

> [!TIP]
> 
> 建议启动前利用 Postman 等 API 测试工具测试运行本项目的计算机与 Zerolan Core 的连接是否正常。Zerolan Live Robot 会在管线连接出错时提供一些建议，仍需要您手动排查。

使用以下命令运行 Zerolan Live Robot 的主程序：

```shell
python main.py
```

### * Minecraft 支持

> [!NOTE]
> 
> 此步骤是**可选**的。

本项目与 [KonekoMinecraftBot](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot) 共同实现了一套接口，可以从本项目控制在 Minecraft 游戏中的机器人。如有需要请移步至[此处](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot)查看详细。


## 自定义设计机器人

Zerolan Live Robot 1.0 旧版本使用的是简单的按秒轮询，从各个服务模块中的缓存列表中读取环境信息。而在 Zerolan Live Robot 2.0 旧版本，转而使用**事件驱动**的设计模式。

### EventEmitter

在本项目中，机器人是在一系列事件的发送和处理过程中运行的。换句话说，没有事件发生，机器人就不会有任何回应。

每一个事件 `Event` 包含一个事件名，本质上是一个字符串。本项目中使用的所有事件名都定义在 `common.enumerator.EventEnum` 中，您也可以拓展添加自己的事件名。我们以处理用户输入语音这个事件为例，它的事件名为 `EventEnum.SERVICE_VAD_SPEECH_CHUNK`。

`emitter` 是一个全局对象，用以处理事件发送和监听器的执行，`emitter` 始终拥有主线程，然而整个系统的运行过程中会有多个线程同时运行，因为每个线程可能都有属于自己的 EventEmitter 的实例。

使用装饰器 `@emitter.on(EventEnum.某个事件)` 可以快捷地注册某个监听器。监听器既可以是同步函数，也可以是异步函数。当我们需要发送事件时，可以使用异步方法 `emitter.emit(EventEnum.某个事件, *args, **kwargs)`。

例如，当系统检测到一段人声音频时，将会发送 `SERVICE_VAD_SPEECH_CHUNK` 事件，并调用所有注册这个事件的监听器，进行某种处理：

```python
@emitter.on(EventEnum.SERVICE_VAD_SPEECH_CHUNK)
async def on_service_vad_speech_chunk(speech: bytes, channels: int, sample_rate: int):
    response = ... # 假设这里获得了语音识别的结果
    await emitter.emit(EventEnum.PIPELINE_ASR, response) # 发送自动语音识别事件
```

这里的监听器即 `on_service_vad_speech_chunk`，本质上是一个函数，它会在 `SERVICE_VAD_SPEECH_CHUNK` 发生时被调用，并接受几个参数，这里的参数完全由事件发送方规定。

### Pipeline

管线（Pipeline）是沟通 Zerolan Core 的重要实现。管线的使用非常简单，只需要传入一个配置对象，就可以得到一个可用的管线对象。然后调用管线对象中的 `predict` 或 `stream_predict` 方法即可使用 Zerolan Core 中的 AI 模型。

以大语言模型为例，指定目标服务器的地址（你的 Zerolan Core 开放端口的地址），传入 `LLMPipelineConfig` 对象到 `LLMPipeline`，即可建立管线。

```python
config = LLMPipelineConfig(server_url="...")
llm = LLMPipeline(config)
query = LLMQuery(text="你好，你叫什么名字？", history=[])
prediction = llm.predict(query)
print(prediction.response)
```

这样就应该可以得到模型的回复。

如果你想知道更多实现细节，可以查看 Zerolan Data 中的数据定义，可能也需要结合管线的实现和 Zerolan Core 中 `app.py` 文件中的内容进行理解。简单来说，它们都是基于 HTTP 的。

### Services

| 模块        | 作用                       | 支持内容                                                     |
| ----------- | -------------------------- | ------------------------------------------------------------ |
| browser     | 基于 Selenium 的浏览器控制 | Firefox 的打开浏览器、搜索和关闭浏览器                       |
| device      | 麦克风、截屏、扬声器控制   | 仅在 Windows 测试过                                          |
| filter      | 对话屏蔽器                 | 简单的匹配过滤器                                             |
| game        | 游戏控制插件               | 详见 [KonekoMinecraftBot](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot) |
| live_stream | 直播平台的弹幕读取         | Bilibili、Twitch、Youtube                                    |
| vad         | 人声音频检测               | 基于能量阈值的音频检测机制                                   |

## 常见问题

### 模型服务启动失败

启动后日志显示“在其上下文中，该请求的地址无效。”。

解决方案，检查配置文件中，`host` 的配置是否正确。如果想要仅本机访问，请指定为 `'127.0.0.1'`。

## License

本项目使用 MIT License，请勿将本软件用于非法用途。

Feel free to enjoy open-souce!

MIT License

Copyright (c) 2024 AkagawaTsurunaki

## Contact with Me

**Email**: AkagawaTsurunaki@outlook.com

**Github**: AkagawaTsurunaki

**Bilibili**: [赤川鹤鸣_Channel](https://space.bilibili.com/1076299680)
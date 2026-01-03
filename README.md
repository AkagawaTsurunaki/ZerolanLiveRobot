# Zerolan Live Robot

![Static Badge](https://img.shields.io/badge/Python%20-%203.10%20-%20blue) ![Static Badge](https://img.shields.io/badge/License-MIT-orange) ![Static Badge](https://img.shields.io/badge/AI%20VTuber-blue) ![Static Badge](https://img.shields.io/badge/Bilibli-fb7299) ![Static Badge](https://img.shields.io/badge/Youtube-ff0000) ![Static Badge](https://img.shields.io/badge/Twitch-9044fe) ![Static Badge](https://img.shields.io/badge/ASR-purple) ![Static Badge](https://img.shields.io/badge/LLM-purple) ![Static Badge](https://img.shields.io/badge/TTS-purple) ![Static Badge](https://img.shields.io/badge/OCR-purple) ![Static Badge](https://img.shields.io/badge/ImageCaptioning-purple) ![Static Badge](https://img.shields.io/badge/VideoCaptioning-purple) ![Static Badge](https://img.shields.io/badge/MinecraftAIAgent-purple) ![Static Badge](https://img.shields.io/badge/ver-2.1.2-green)

你或许已经听说过著名的 [Neurosama](https://virtualyoutuber.fandom.com/wiki/Neuro-sama)，或者是来自中国的[木几萌](https://mobile.moegirl.org.cn/%E6%9C%A8%E5%87%A0%E8%90%8C)。你是否也想要拥有一个自己的 AI 虚拟形象陪你直播、聊天、打游戏？开源的 Zerolan Live Robot 正致力于实现您的梦想！而这仅仅需要一张消费级显卡！

Zerolan Live Robot 是一款多功能的直播机器人（AI VTuber），它可以听懂你所说的话，也可以自动在直播间中读取弹幕，观察电脑屏幕的指定窗口，理解其画面内容和文字信息，操纵 Minecraft 中的游戏角色，做出带情感的语音聊天回应。

相关项目：[KonekoMinecraftBot](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot)、[ZerolanCore](https://github.com/AkagawaTsurunaki/zerolan-core)、[ZerolanData](https://github.com/AkagawaTsurunaki/zerolan-data)、[ZerolanPlayground](https://github.com/AkagawaTsurunaki/ZerolanPlayground)。

本项目持续开发中，当前的版本为 `2.1.2`，您可以关注开发者的 Bilibili 账号[赤川鹤鸣_Channel](https://space.bilibili.com/1076299680)，正在根据此项目调教 AI 猫娘，不定时直播展示最新进展。

## 特点与功能

- [x] 💭 基于大语言模型的自然语言对话，上下文理解和人机聊天
- [x] 🍻 连接至 Bilibili、YouTube（实验）、Twitch（实验）直播间，根据弹幕内容挑选并回复
- [x] 🎙️ 识别用户麦克风语音输入内容，理解并回复（例如：`你叫什么名字？`、`请关闭麦克风！`）
- [x] 📣 根据回复文本的带情感的语音合成
- [x] 📄 识别指定窗口中的文字内容，并分析其中的文字（例如：`能看见这里写了什么吗？`）
- [x] 🖼️ 识别指定窗口中的图像内容，并理解其中的含义（例如：`你看见了什么东西？`）
- [x] 🔍️ 打开、控制浏览器并执行百科搜索（例如：`搜索一下什么是二次元。`）
- [x] 🖱️ 语音指令控制鼠标点击 UI 界面（例如：`点击屏幕上的搜索按钮`）
- [x] 🛠️ 根据上下文语境采取行动或挑选工具（例如：`好了，你可以关机了！`、`请关闭浏览器`）
- [x] 🎮️ 语音指令可控制的 Minecraft AI 智能体（例如：`在游戏中跟大家说你好！`）
- [x] 📓 基于最大记录条数的简单的运行时上下文短期记忆
- [x] 📖 基于 向量数据库的长期记忆存储与提取（例如：`你还记得我说过春日影是什么嘛？`）
- [x] 🎞️ OBS 直播流式打字机字幕显示与控制
- [x] ⚙️ 系统配置和实时控制器的 WebUI 界面
- [x] 🥳 Live2D 形象控制，嘴型同步、自动眨眼和自主呼吸
- [x] 基于 Unity 的 Live2D 形象控制和 3D 模型控制的展示应用

## 安装并运行

> [!CAUTION]
>
> Zerolan Live Robot 2.x 版本与旧版本 1.x 不兼容，因此您可能需要重新配置环境、安装依赖。

Zerolan Project 由 [ZerolanLiveRobot](https://github.com/AkagawaTsurunaki/ZerolanLiveRobot)、[ZerolanCore](https://github.com/AkagawaTsurunaki/zerolan-core)、[ZerolanData](https://github.com/AkagawaTsurunaki/zerolan-data)、[ZerolanPlayground](https://github.com/AkagawaTsurunaki/ZerolanPlayground)、[KonekoMinecraftBot](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot) 等项目共同组成。下表简要地介绍了各个项目的用途，您可以根据需要使用：

| 项目名                                                       | 用途                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [ZerolanLiveRobot](https://github.com/AkagawaTsurunaki/ZerolanLiveRobot) | 直播机器人的控制框架，通过采集各类数据，并综合分析做出动作响应。 |
| [ZerolanCore](https://github.com/AkagawaTsurunaki/zerolan-core) | 为直播机器人提供 AI 推理服务的核心模块，例如大语言模型、语音识别、语音合成等 Web API 服务。 |
| [ZerolanData](https://github.com/AkagawaTsurunaki/zerolan-data) | 定义了各个项目或服务之间沟通与交换的数据格式。               |
| [ZerolanPlayground](https://github.com/AkagawaTsurunaki/ZerolanPlayground)                                        | 使用 Unity 引擎和 Vuforia 引擎开发的 AR 虚拟形象展示器，兼容 Live2D 模型的展示。|
| [KonekoMinecraftBot](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot) | 基于 mineflayer 的 Minecraft 智能体，使用有限状态机控制行为（打怪、砍树、睡觉等），支持语音控制。 |

### 部署核心服务

如果你希望将 AI 模型服务部署在自己的电脑上，请移步至[此处](https://github.com/AkagawaTsurunaki/zerolan-core)进完成 ZerolanCore 的相关部署工作。

本项目提供了一些第三方提供的 API 接口的支持，但如果其中没有你想要的，请根据文档实现自己的统一模型管线（Unified Model Pipeline, UMP）。

当然，您可以根据需求混合使用第三方接口和 ZerolanCore 服务，后续您可以在配置文件中设置。

无论如何，你必须至少配置**大语言模型**才能驱动整个项目，它是驱动本项目的核心。

### 安装本项目依赖

如果你使用的是 Windows 操作系统，且正在使用较高版本的 Python，请检查您是否已经安装了 [Visual C++ Build Tools](https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/)，部分 Python 依赖的库可能会需要在您的操作系统上编译后安装。当然，更推荐您使用较低版本的 Python，例如 `3.10` 和 `3.11`。

运行指令，这会创建一个虚拟环境并激活，然后自动安装本项目需要的依赖包：

```shell
conda create --name ZerolanLiveRobot python=3.11
conda activate ZerolanLiveRobot
pip install -r requirements.txt
```

### 配置并启动本项目

使用以下命令运行 Zerolan Live Robot 的主程序：

```shell
python main.py
```

如果你是第一次启动本项目，主程序将为您自动生成一份配置文件，位置在你的项目目录下的 `./resources/config.yaml`，最后会自动退出，这是正常现象。

这样，你有两种方式修改你的配置文件：

1. WebUI配置：运行 `python webui.py` 将会启动一个 WebUI 的配置界面，你可以在浏览器中访问它（通常是`http://127.0.0.1:7860`），然后根据配置项中的描述和提示进行填写，填写完毕后，可以单击右上角的 Save Config 按钮，这将保存配置到 `./resources/config.yaml`。
2. 手动修改：直接找到 `./resources/config.yaml` 文件并按照文件内的注释引导填写对应的配置。

若在此期间出现任何报错或问题，都可以通过新建 Issue 获取帮助，届时还恳请您提供完整的日志和复现流程。

### * Minecraft 支持

> [!NOTE]
> 
> 此步骤是**可选**的。

本项目与 [KonekoMinecraftBot](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot) 共同实现了一套 ZerolanProtocol 协议接口，可以从本项目控制在 Minecraft 游戏中的机器人。如有需要请移步至[此处](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot)查看详细。

###  * Zerolan Playground

> [!NOTE]
> 
> 此步骤是**可选**的。因为本项目已经支持了 Live2D 的展示功能，如果你需要 AR 等基于 Unity 和 Vuforia 的功能请继续向下阅览。

下载对应平台的安装包进行安装，然后在右上角填写你开启本 ZerolanLiveRobot 的服务器地址。

例如，你将 ZerolanLiveRobot 主程序开启在你的电脑的 11013 端口，且你的电脑 IP 为 `192.168.1.114`，那么在服务器地址一栏填写 `ws://192.168.1.114:11013`，最后单击“连接”即可。


## 自定义设计机器人

本项目也提供了一种基于**事件驱动**设计模式的机器人开发框架。它的核心是 `TypedEventEmitter`。

### TypedEventEmitter

在本项目中，机器人是在一系列事件的发送和处理过程中运行的。换句话说，没有事件发生，机器人就不会有任何回应。

每一个事件 `Event` 都继承自 `BaseEvent`，并含有一个 `type` 字段（字符串类型）用以标记这个事件的类型。本项目中使用的所有事件类型的都定义在 `event.registry` 中，您也可以拓展添加自己的事件名，并实现一个继承自 `BaseEvent` 的自定义事件 。

`emitter` 是一个全局对象，用以处理事件发送和监听器的执行。

使用装饰器 `@emitter.on(event_key)` 可以快捷地注册某个监听器。当监听器是异步函数时，会在触发事件时以异步协程任务的形式执行；当监听器是同步函数时，会在触发事件时将在一个默认 4 个 worker 的线程池中执行。

> [!Caution]
>
> 由于 `emitter` 开启的事件循环运行在主线程上，因此**不要使用任何可能阻塞主线程的方法或函数**，除非你知道你在做什么。、
>
> 同步监听器运行在线程池上，请注意**线程安全**问题，你也可以自行调整 worker 的数量。

当我们需要发送事件时，可以使用 `emitter.emit(event)`，其中 `event` 就是一个 `BaseEvent` 事件对象。

例如，当系统检测到一段人声音频时，将会发送 `SpeechEvent` 事件（其 `event_key` 为 `EventKeyRegistry.Device.SERVICE_VAD_SPEECH_CHUNK` 所代表的字符串），并调用所有注册这个事件的监听器，进行某种处理：

```python
@emitter.on(EventKeyRegistry.Device.MICROPHONE_VAD)
async def on_service_vad_speech_chunk(event: SpeechEvent):
    speech, channels, sample_rate = event.speech, event.channels, event.sample_rate
    prediction = await asr.predict(...)  # 假如调用了某个函数获得了 ASR 的结果
    emitter.emit(ASREvent(prediction=prediction))  # 发送自动语音识别事件
```

这里的监听器即 `on_service_vad_speech_chunk`，本质上是一个函数，它会在 `SpeechEvent` 发生时被调用。

### Pipeline

管线（Pipeline）是沟通 Zerolan Core 的重要实现，它是基于 HTTP 开发的。管线的使用非常简单，只需要传入一个配置对象，就可以得到一个可用的管线对象。然后调用管线对象中的 `predict` 或 `stream_predict` 方法即可使用 Zerolan Core 中的 AI 模型，当然也包括一些第三方的 API。

以大语言模型为例，指定目标服务器的地址（你的 Zerolan Core 服务开启的地址），传入 `LLMPipelineConfig` 对象到 `LLMPipeline`，即可建立管线。

```python
config = LLMPipelineConfig(predict_url="http://127.0.0.1:11000/llm/predict")
llm = LLMPipeline(config)
query = LLMQuery(text="你好，你叫什么名字？", history=[])
prediction = llm.predict(query)
print(prediction.response)
# 这样就应该可以得到模型的回复
```

如果你想知道更多实现细节，可以查看 [ZerolanData](https://github.com/AkagawaTsurunaki/zerolan-data) 中的数据定义，可能也需要结合管线的实现和 [ZerolanCore](https://github.com/AkagawaTsurunaki/zerolan-core) 中 `app.py` 文件中的内容进行理解。

### Services

### services.browser

基于 Selenium 的简单的浏览器控制器。仅支持 `Firefox`。
功能很简单，如果需要扩展需要自己实现。其中机器人可能会使用 ShowUI 的模型推理结果来调用并控制浏览器。

### services.game

用于与其它游戏进行连接和游玩的控制器。目前仅支持 Minecraft 平台。

### services.live2d

基于 [live2d-py](https://github.com/Arkueid/live2d-py)、[OpenGL](https://www.opengl.org/) 和 
[PyQt5](https://pypi.org/project/PyQt5/) 开发的 Live2D 虚拟形象控制器。
实现了窗口宽高控制、透明背景（可用于 OBS 直播或桌宠），角色自动呼吸控制、自动眨眼控制，说话时嘴型控制。

### services.live_stream

连接到指定直播平台服务，获取弹幕、礼物消息等。支持 Bilibili、YouTube（实验）、Twitch（实验）直播间。

### services.obs

OBS 直播流式打字机字幕显示与控制，基于 [OBSWebSocket](https://github.com/obsproject/obs-websocket) 实现。

> [!NOTE]
> 您需要开启 OBS 的 WebSocket 服务器。步骤如下：
> 1. 打开 OBS。
> 2. 找到工具栏中的“工具”选项，选择“WebSocket 服务器设置”。
> 3. 点击“生成密码”设置服务器密码。
> 4. 点击“显示连接信息”。
> 5. 将服务器 IP 、服务器端口和服务器密码填写入配置文件。

### services.playground

Zerolan Playground Server 是一个基于 ZerolanProtocol 的 WebSocket 服务器，用于与 Unity 实现的 Zerolan Playground 进行连接和交互。

### services.qqbot

正在开发中……



## License

本项目使用 MIT License，请勿将本软件用于非法用途。

Feel free to enjoy open-souce!

MIT License

Copyright (c) 2024 AkagawaTsurunaki

## Contact with Me

**Email**: AkagawaTsurunaki@outlook.com

**Github**: AkagawaTsurunaki

**Bilibili**: [赤川鹤鸣_Channel](https://space.bilibili.com/1076299680)

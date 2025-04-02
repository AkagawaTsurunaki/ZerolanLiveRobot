# Zerolan Live Robot

![Static Badge](https://img.shields.io/badge/Python%20-%203.10%20-%20blue) ![Static Badge](https://img.shields.io/badge/License-MIT-orange) ![Static Badge](https://img.shields.io/badge/AI%20VTuber-blue) ![Static Badge](https://img.shields.io/badge/Bilibli-fb7299) ![Static Badge](https://img.shields.io/badge/Youtube-ff0000) ![Static Badge](https://img.shields.io/badge/Twitch-9044fe) ![Static Badge](https://img.shields.io/badge/ASR-purple) ![Static Badge](https://img.shields.io/badge/LLM-purple) ![Static Badge](https://img.shields.io/badge/TTS-purple) ![Static Badge](https://img.shields.io/badge/OCR-purple) ![Static Badge](https://img.shields.io/badge/ImageCaptioning-purple) ![Static Badge](https://img.shields.io/badge/VideoCaptioning-purple) ![Static Badge](https://img.shields.io/badge/MinecraftAIAgent-purple) ![Static Badge](https://img.shields.io/badge/ver-2.1-green)

你或许已经听说过著名的 [Neurosama](https://virtualyoutuber.fandom.com/wiki/Neuro-sama)，或者是来自中国的[木几萌](https://mobile.moegirl.org.cn/%E6%9C%A8%E5%87%A0%E8%90%8C)。你是否也想要拥有一个自己的 AI 虚拟形象陪你直播、聊天、打游戏？开源的 Zerolan Live Robot 正致力于实现您的梦想！而这仅仅需要一张消费级显卡！

Zerolan Live Robot 是一款多功能的直播机器人（AI VTuber），它可以听懂你所说的话，也可以自动在直播间中读取弹幕，观察电脑屏幕的指定窗口，理解其画面内容和文字信息，操纵 Minecraft 中的游戏角色，做出带情感的语音聊天回应。

相关项目：[KonekoMinecraftBot](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot)、[ZerolanCore](https://github.com/AkagawaTsurunaki/zerolan-core)、[ZerolanData](https://github.com/AkagawaTsurunaki/zerolan-data)、[ZerolanUI](https://github.com/AkagawaTsurunaki/zerolan-ui)。

> [!Note]
>
> 本项目持续开发中，当前的版本为 `2.x`，您可以关注开发者的 Bilibili 账号[赤川鹤鸣_Channel](https://space.bilibili.com/1076299680)，正在根据此项目调教 AI 猫娘，不定时直播展示最新进展。

## 特点与功能

- [x] 💭 基于大语言模型的自然语言对话
- [x] 🍻 根据直播间弹幕挑选并回复
- [x] 🎙️ 识别用户麦克风语音输入内容，理解并回复（例如：`你叫什么名字？`、`请关闭麦克风！`）
- [x] 📣 根据回复文本的带情感的语音合成
- [x] 📄 识别指定窗口中的文字内容，并分析其中的文字（例如：`能看见这里写了什么吗？`）
- [x] 🖼️ 识别指定窗口中的图像内容，并理解其中的含义（例如：`你看见了什么东西？`）
- [x] 🔍️ 打开、控制浏览器并执行百科搜索（例如：`搜索一下什么是二次元。`）
- [x] 🖱️ 语音指令控制鼠标点击 UI 界面
- [x] 🛠️ 根据上下文语境采取行动或挑选工具（例如：`好了，你可以关机了！`、`请关闭浏览器`）
- [x] 🎮️ 根据语音指令控制 Minecraft AI 智能体（例如：`在游戏中跟大家说你好！`）
- [x] 📓 基于最大记录条数的简单的运行时上下文短期记忆
- [x] 📖 基于向量数据库的长期记忆存储与提取（例如：`你还记得我说过春日影是什么嘛？`）
- [x] Live2D + AR 形象的控制（ZerolanPlayground 开发基本完毕，已进入测试阶段） 
- [x] 🎞️ OBS 直播流式字幕显示（OBS-WebSocket 实现）

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
| 视觉语言模型代理 | [showlab/ShowUI](https://github.com/showlab/ShowUI)          |
| 外部可调用工具   | 火狐浏览器、百度百科、萌娘百科                               |
| 游戏插件         | Minecraft                                                    |

## 安装并运行

> [!CAUTION]
>
> Zerolan Live Robot 2.x 版本与旧版本 1.x 不兼容，因此您可能需要重新配置环境、安装依赖。

Zerolan 框架由 [ZerolanLiveRobot](https://github.com/AkagawaTsurunaki/ZerolanLiveRobot)、[ZerolanCore](https://github.com/AkagawaTsurunaki/zerolan-core)、[ZerolanData](https://github.com/AkagawaTsurunaki/zerolan-data)、[ZerolanUI](https://github.com/AkagawaTsurunaki/zerolan-ui)。 共同组成。下表简要地介绍了各个项目的用途：

| 项目名                                                       | 用途                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [ZerolanLiveRobot](https://github.com/AkagawaTsurunaki/ZerolanLiveRobot) | 直播机器人的控制框架，通过采集环境数据，并综合分析做出动作响应。 |
| [ZerolanCore](https://github.com/AkagawaTsurunaki/zerolan-core) | 为直播机器人提供 AI 推理服务的核心模块，例如大语言模型的 Web API 服务化。 |
| [ZerolanData](https://github.com/AkagawaTsurunaki/zerolan-data) | 定义各个服务之间利用网络请求交换的数据格式。                 |
| [ZerolanUI](https://github.com/AkagawaTsurunaki/zerolan-ui)  | 基于 PyQT6 的 GUI 界面，包括顶部弹窗和提示音等。             |

### 部署核心服务

> [!IMPORTANT]
>
> 此步骤是**必须**的！你必须至少配置大语言模型才能驱动整个项目。

请移步至[此处](https://github.com/AkagawaTsurunaki/zerolan-core)进完成 ZerolanCore 的相关部署工作，ZerolanLiveRobot 强依赖于此核心服务。

### 安装本项目依赖

运行指令，这会创建一个虚拟环境并激活，然后自动安装本项目需要的依赖包：

```shell
conda create --name ZerolanLiveRobot python=3.10
conda activate ZerolanLiveRobot
pip install -r requirements.txt
```

如果您在 `main` 主分支，那么依赖 [ZerolanData](https://github.com/AkagawaTsurunaki/zerolan-data)、[ZerolanUI](https://github.com/AkagawaTsurunaki/zerolan-ui) 可以从 pypi 自动安装。

而如果您在 `dev` 开发分支，您可能需要手动安装：

```shell
pip install git+https://github.com/AkagawaTsurunaki/zerolan-ui.git@dev
pip install git+https://github.com/AkagawaTsurunaki/zerolan-data.git@dev
```

### 修改配置

找到 `resources/config.template.yaml` 配置文件，直接在当前目录复制一份，并更名为 `config.yaml` ，然后根据配置文件中的注释修改为您需要的配置。

### 启动本项目

使用以下命令运行 Zerolan Live Robot 的主程序：

```shell
python main.py
```

若出现任何警告或者报错，请先查看文档底部的常见问题，如果这不能为您提供足够的帮助，可以新建 Issue。

### * Minecraft 支持

> [!NOTE]
> 
> 此步骤是**可选**的。

本项目与 [KonekoMinecraftBot](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot) 共同实现了一套接口，可以从本项目控制在 Minecraft 游戏中的机器人。如有需要请移步至[此处](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot)查看详细。


## 自定义设计机器人

Zerolan Live Robot 1.0 旧版本使用的是简单的按秒轮询，从各个服务模块中的缓存列表中读取环境信息。而在 Zerolan Live Robot 2.0 旧版本，转而使用**事件驱动**的设计模式。

### EventEmitter

在本项目中，机器人是在一系列事件的发送和处理过程中运行的。换句话说，没有事件发生，机器人就不会有任何回应。

每一个事件 `Event` 都继承自 `BaseEvent`，并含有一个 `type` 字段（字符串类型）用以标记这个事件的类型。本项目中使用的所有事件类型的都定义在 `event.registry` 中，您也可以拓展添加自己的事件名，并实现一个继承自 `BaseEvent` 的自定义事件 。

`emitter` 是一个全局对象，用以处理事件发送和监听器的执行，`emitter` 始终拥有主线程，然而整个系统的运行过程中会有多个协程任务被创建和销毁。

使用装饰器 `@emitter.on(event_key)` 可以快捷地注册某个监听器。当监听器是异步函数时，会在触发事件时以协程任务的形式执行；当监听器是同步函数时，会在额外的线程中按注册的先后同步顺序执行（这不会阻塞主线程）。

当我们需要发送事件时，可以使用 `emitter.emit(event_key)`，其中 `event` 就是一个事件对象。

例如，当系统检测到一段人声音频时，将会发送 `SpeechEvent` 事件（其 `event_key` 为 `EventKeyRegistry.Device.SERVICE_VAD_SPEECH_CHUNK` 所代表的字符串），并调用所有注册这个事件的监听器，进行某种处理：

```python
@emitter.on(EventKeyRegistry.Device.SERVICE_VAD_SPEECH_CHUNK)
async def on_service_vad_speech_chunk(event: SpeechEvent):
    speech, channels, sample_rate = event.speech, event.channels, event.sample_rate
    prediction = ... # 假如调用了某个函数获得了 ASR 的结果
    emitter.emit(ASREvent(prediction=prediction)) # 发送自动语音识别事件
```

这里的监听器即 `on_service_vad_speech_chunk`，本质上是一个函数，它会在 `SpeechEvent` 发生时被调用。

### Pipeline

管线（Pipeline）是沟通 Zerolan Core 的重要实现，它是基于 HTTP 开发的。管线的使用非常简单，只需要传入一个配置对象，就可以得到一个可用的管线对象。然后调用管线对象中的 `predict` 或 `stream_predict` 方法即可使用 Zerolan Core 中的 AI 模型。

以大语言模型为例，指定目标服务器的地址（你的 Zerolan Core 开放端口的地址），传入 `LLMPipelineConfig` 对象到 `LLMPipeline`，即可建立管线。

```python
config = LLMPipelineConfig(server_url="...")
llm = LLMPipeline(config)
query = LLMQuery(text="你好，你叫什么名字？", history=[])
prediction = llm.predict(query)
print(prediction.response)
# 这样就应该可以得到模型的回复
```

如果你想知道更多实现细节，可以查看 Zerolan Data 中的数据定义，可能也需要结合管线的实现和 Zerolan Core 中 `app.py` 文件中的内容进行理解。

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

### 启动时报错

**Q：**启动时报错：

```
Are you sure that you have copied `config.yaml` from `config.template.yaml` in `resources`?`
```

**A：**原因是您没有将配置文件放在正确的位置。假如你的项目文件夹放在了 `C:/ZerolanLiveRobot/`，那么你应该检查 `C:/ZerolanLiveRobot/resources/config.yaml` 是否存在，然后按照先前的文档进行配置即可。

---

**Q：**启动时报错

```
Room id must be greater than 0
```

**A：**默认的配置文件中 Bilibili 的直播间号设置了一个非法值，您需要配置您指定的目标直播间号。

---

**Q：**启动项目时报错：

```
You have enabled `live_stream`, but none of the platforms have been successfully connected.
```

**A：**您启动了直播间服务后，会尝试连接所有的平台，并自动选出其中可以成功连接的那些平台。出现这个错误代表着任何一个平台的连接都失败了，可能原因是您的配置文件有问题，也可能是网络连接不良，还有可能是因为官方的 API 接口发生了变更。

另外注意的是，在配置文件中，只需要修改对应的您想使用的直播平台的配置项，您不需要的直播平台配置项请保留空字符串，不要尝试删除它们。

---

**Q：**启动时报错：

```
Are you sure that you have configurated your TTS prompts directory?
```

**A：**这是因为您没有指定 TTS 提示音频的存放目录，或者你指定的目录不存在，请到配置文件中检查并修改，请使用**绝对路径**。

---

**Q：**启动时报错：

```
There are no eligible TTS prompts in the directory you provided.
```

**A：**出现这种情况，证明项目中的 TTS 提示音频的存放目录已经可达，但是里面没有音频文件，或者所有的音频文件都不符合命名规则，详细见上文配置一节。

**Q：**启动时报警告：

```
No suitable filename parsing strategy, the audio file will skip: ...
```

**A：**这是因为该文件的命名格式不正确，会被跳过，警告不影响项目的运行。针对命名规则，请在文档配置一节找到详细的 TTS prompt 命名规则。

### 运行时报错

**Q：**运行时报错

```
由于目标计算机积极拒绝，无法连接。
```

**A：**检查你的配置文件中目标服务器的地址是否正确，端口是否正确，以及是否有防火墙阻止了连接，或者使用了服务器的访问权限控制。如果你的目标服务器就是本机，那么很有可能是因为你的服务根本没有开启。

## License

本项目使用 MIT License，请勿将本软件用于非法用途。

Feel free to enjoy open-souce!

MIT License

Copyright (c) 2024 AkagawaTsurunaki

## Contact with Me

**Email**: AkagawaTsurunaki@outlook.com

**Github**: AkagawaTsurunaki

**Bilibili**: [赤川鹤鸣_Channel](https://space.bilibili.com/1076299680)
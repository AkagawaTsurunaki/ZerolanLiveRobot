# Zerolan Live Robot

![Static Badge](https://img.shields.io/badge/Python%20-%203.10%20-%20blue) ![Static Badge](https://img.shields.io/badge/Node%20-%2020.9.0%20-%20violet) ![Static Badge](https://img.shields.io/badge/CUDA%20-%202.1.1%2Bcu118%20-%20green) ![Static Badge](https://img.shields.io/badge/License%20-%20GPLv3%20-%20orange) 

![Static Badge](https://img.shields.io/badge/AI%20VTuber%20-%20green) ![Static Badge](https://img.shields.io/badge/Bilibli%20Live%20-%20green) ![Static Badge](https://img.shields.io/badge/Large%20Language%20Model%20-%20green) ![Static Badge](https://img.shields.io/badge/Text%20to%20Speech%20-%20green) ![Static Badge](https://img.shields.io/badge/Image%20to%20Text%20-%20green) ![Static Badge](https://img.shields.io/badge/Minecraft%20AI%20Agent%20-%20green) ![Static Badge](https://img.shields.io/badge/Automatic%20Speech%20Recognition%20%20-%20green)

*Docs Languages: [简体中文](https://github.com/AkagawaTsurunaki/ZerolanLiveRobot/blob/main/README.md) | [English](https://github.com/AkagawaTsurunaki/ZerolanLiveRobot/blob/main/docs/en/README.md) | [日本語](https://github.com/AkagawaTsurunaki/ZerolanLiveRobot/blob/main/docs/ja/README.md)*

基于大语言模型、计算机视觉、语音合成、语音识别人工智能技术的虚拟形象直播机器人。

你或许已经听说过著名的 [Neurosama](https://virtualyoutuber.fandom.com/wiki/Neuro-sama)，或者是来自中国的[木几萌](https://mobile.moegirl.org.cn/%E6%9C%A8%E5%87%A0%E8%90%8C)。 

目前，越来越多的 AI VTuber 广泛地出现在 Twitch、Youtube、Bilibili 等平台，这些 AI VTuber 可以与直播间的观众互动、闲聊、看视频、打游戏等操作。同时，也有更多的公司正在基于 AI 等技术开发相关的直播机器人。这些虚拟形象通常覆盖了直播、游戏、娱乐等广泛的服务范围。

本人希望能让世界上每一个人，可在消费级显卡上部署一个 AI 虚拟形象，你可以将其作为自己的朋友、伴侣，或任何您想让 TA 成为的形象，融入您的日常生活，在赛博世界中永远陪伴着你。

## 项目功能

| 功能                 | 描述                                                         |
| -------------------- | ------------------------------------------------------------ |
| 纯文本对话           | 利用大语言模型，可以对环境做出响应，输出文本内容。           |
| 带情感切换的语音对话 | 利用 TTS 模型和基于文本语气的提示词切换机制，可以根据输出文本内容和当前的心情合成带有语气的语音片段。 |
| 语音识别             | 利用 ASR 模型，可以识别来自现实环境中的人类声音。            |
| 视觉识别             | 利用图像识别模型，可以根据来自指定窗口的截图，理解图像内容。 |
| 直播平台接入         | 利用各大直播平台的 API，可以读取来自直播间的弹幕等信息。     |
| 游戏智能体插件       | 目前支持 Koneko，可以与本项目一同使用用以连接 Minecraft AI 智能体，使其具有打游戏的功能。 |

## 支持模型

为了能够使更多的人可以在本地部署本项目，目前测试了一系列的开源人工智能模型。

### 大语言模型

| 模型名称                                                     | 语言支持    | 显存占用      | 描述     |
| ------------------------------------------------------------ | ----------- | ------------- | -------- |
| [THUDM/chatglm3-6b](https://huggingface.co/THUDM/chatglm3-6b) | ✅中 ✅英 ❌日 | 5.4GB (4-bit) | 支持量化 |
| [Qwen/Qwen-7B-Chat](https://huggingface.co/Qwen/Qwen-7B-Chat) | ✅中 ✅英 ❌日 | -             | 支持量化 |
| [01-ai/Yi-6B-Chat](https://huggingface.co/01-ai/Yi-6B-Chat)  | ✅中 ✅英 ❌日 | -             |          |
| [augmxnt/shisa-7b-v1](https://huggingface.co/augmxnt/shisa-7b-v1) | ❌中 ✅英 ✅日 | 11.6GB        |          |

### 文本转语音模型

| 模型名称                                                     | 语言支持    | 显存占用 | 描述                   |
| ------------------------------------------------------------ | ----------- | -------- | ---------------------- |
| [RVC-Boss/GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) | ✅中 ✅英 ✅日 | -        | 语音克隆 \| 文本转语音 |

### 视觉模型

| 模型名称                                                     | 类型              | 显存占用 | 描述 |
| ------------------------------------------------------------ | ----------------- | -------- | ---- |
| [Salesforce/blip-image-captioning-large](https://huggingface.co/Salesforce/blip-image-captioning-large) | Image captionning | -        | -    |

### 自动语音识别模型

| 模型名称         | 语言支持    | 显存占用 | 描述 |
| ---------------- | ----------- | -------- | ---- |
| SpeechParaformer | ✅中 ✅英 ✅日 | -        |      |

## 背景

> 这一部分是对本项目的由来的阐述，可以更好地让您了解项目的成长过程。

2022 年末至 2023 年初，此时正值人工智能模型，尤其是大语言模型的爆火时期，我也有幸体验到了诸如 [ChatGPT](https://openai.com/chatgpt) 等基于大语言模型的应用。虽然其具有一定逻辑和专业知识的对话体验深深震撼了我，然而当时的我却没有意识到这其实是虚拟主播世界的一次基于人工智能变革的前夕。

在 2023 年，本人第一次接触到 [Neurosama](https://virtualyoutuber.fandom.com/wiki/Neuro-sama) 的时候，为其可爱的外表、有趣的对话和行为所吸引。在观看了相当一部分的切片视频后，我越发对其背后的实现机理和架构着迷，于是在 2023 年末，我开启了第一次的尝试，并将此项目命名为 LingController。

无论是从直播间读取弹幕等信息，还是获取现实世界中人类发出的语音，对于大语言模型来说，无非是将一段文字转换为另一段文字。因此，不难想到将大语言模型作为整个项目的核心模块。通过语音识别模块，我们可以将一段来自外界的语音转录为一段纯文本，并将其输入给大语言模型，而大语言模型的输出文字将会被传递给一个文字转语音模型。

在当时，鉴于 GPU 的局限性，我选择了 [THUDM/ChatGLM2-6B](https://github.com/thudm/chatglm2-6b) 作为大语言模型，和当时较为有潜力的文本转语音模型 [Plachtaa/VALL-E-X](https://github.com/Plachtaa/VALL-E-X)（此模型结构原为微软提出），以及百度[飞桨PaddlePaddle](https://www.paddlepaddle.org.cn/) 的一个自动语音识别模型。

大概耗时数周，LingController 最终可以运行，但是存在诸多问题：

1. 由于大语言模型开启量化后精度损失而造成的胡言乱语、言不达意。
2. 合成语音存在频发的吞字、漏字、不清晰以及严重的第二语言问题。
3. 作为一个实验项目，LingController 并没有优良的架构设计。

在 2024 年，全新的语音合成模型的出现，和越来越多的开源大语言模型的应用，使我重新对项目进行了更改。同时为了更好地支持开源社区，我重新创建了这个名为 Zerolan Live Robot 的开源项目，并且增加了更多的功能。

因此在发布了 Zerolan Live Robot 的第一个版本后，我很快意识到了其它问题。

1. 不同的开源仓库或模型使用了不同的接口设计方案，这导致各个模型的信息流交互会随着模型的增加越来越困难。

2. 未来可能会支持更多的游戏智能体，而不局限于 Minecraft。

为了方便开发，我设计了一套通用管线用以处理各个模型之间的交互流，同时将 Minecraft AI 智能体作为一个单独的开源项目 Koneko。我们希望这种管线数据流的模型交互框架可以适用于更多的 AI 模型，以便能为您提供更加多样复杂的底层模型组合和交互方法，最终达成打造更加个性化的交互机器人解决方案。

## 架构设计

环境-智能体

具体地说，对于 Zerolan Live Robot 的外部环境，例如用户的语音输入、文本输入、电脑快照、



## 即将到来

- [ ] 虚拟形象控制
- [ ] 唱歌


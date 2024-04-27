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

### 大语言模型（Large Language Model，LLM）

| 模型                                                         | 语言支持    | 显存占用 | 描述 |
| ------------------------------------------------------------ | ----------- | -------- | ---- |
| [THUDM/chatglm3-6b](https://huggingface.co/THUDM/chatglm3-6b) | ✅中 ✅英 ❌日 |          |      |
| [Qwen/Qwen-7B-Chat](https://huggingface.co/Qwen/Qwen-7B-Chat) | ✅中 ✅英 ❌日 |          |      |
|                                                              |             |          |      |





## 即将到来

- [ ] 虚拟形象控制
- [ ] 唱歌


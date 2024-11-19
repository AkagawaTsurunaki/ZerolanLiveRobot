# Zerolan Live Robot 2.0

![Static Badge](https://img.shields.io/badge/Python%20-%203.10%20-%20blue) ![Static Badge](https://img.shields.io/badge/License-MIT-orange) ![Static Badge](https://img.shields.io/badge/AI%20VTuber-blue) ![Static Badge](https://img.shields.io/badge/Bilibli-fb7299)  ![Static Badge](https://img.shields.io/badge/Twitch-9044fe) ![Static Badge](https://img.shields.io/badge/LLM-purple) ![Static Badge](https://img.shields.io/badge/TTS-purple) ![Static Badge](https://img.shields.io/badge/ImageCaptioning-purple) ![Static Badge](https://img.shields.io/badge/MinecraftAIAgent-purple) ![Static Badge](https://img.shields.io/badge/ASR-purple)

你或许已经听说过著名的 [Neurosama](https://virtualyoutuber.fandom.com/wiki/Neuro-sama)，或者是来自中国的[木几萌](https://mobile.moegirl.org.cn/%E6%9C%A8%E5%87%A0%E8%90%8C)。你是否也想要拥有一个自己的 AI 虚拟形象陪你直播、聊天、打游戏？开源的 Zerolan Live Robot 正致力于实现您的梦想！而这仅仅需要一张消费级显卡！

Zerolan Live Robot 是一款多功能的直播机器人（AI VTuber），它可以自动在 Bilibili 直播间中读取弹幕，观察电脑屏幕的指定窗口，理解其画面内容，操纵
Minecraft 中的游戏角色，做出带情感的语音聊天回应。

与其关联的项目 [KonekoMinecraftBot](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot)、[zerolan-core](https://github.com/AkagawaTsurunaki/zerolan-core)、[zerolan-data](https://github.com/AkagawaTsurunaki/zerolan-data)、[zerolan-ui](https://github.com/AkagawaTsurunaki/zerolan-ui)。

> [!Note]
>
> 本项目持续开发中，当前的版本为 `2.0`，您可以关注开发者的 Bilibili 账号[赤川鹤鸣_Channel](https://space.bilibili.com/1076299680)，正在根据此项目调教 AI 猫娘，不定时直播展示最新进展。

| 支持项           | 支持内容                                                     |
| ---------------- | ------------------------------------------------------------ |
| 直播平台         | [Bilibili](https://www.bilibili.com) \| [Twitch](https://www.twitch.tv) |
| 大语言模型       | [THUDM/GLM-4](https://github.com/THUDM/GLM-4) \| [THUDM/ChatGLM3](https://github.com/THUDM/ChatGLM3) \| [Qwen/Qwen-7B-Chat](https://huggingface.co/Qwen/Qwen-7B-Chat) \| [01ai/Yi-6B-Chat](https://www.modelscope.cn/models/01ai/Yi-6B-Chat) \| [augmxnt/shisa-7b-v1](https://huggingface.co/augmxnt/shisa-7b-v1) |
| 自动语音识别模型 | [iic/speech_paraformer_asr](https://www.modelscope.cn/models/iic/speech_paraformer_asr_nat-zh-cn-16k-common-vocab8358-tensorflow1) |
| 语音合成模型     | [RVC-Boss/GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)         |
| 图像字幕模型     | [Salesforce/blip-image-captioning-large](https://huggingface.co/Salesforce/blip-image-captioning-large) |
| 光学字符识别模型 | [paddlepaddle/PaddleOCR](https://gitee.com/paddlepaddle/PaddleOCR)        |
| 视频字幕模型     | [iic/multi-modal_hitea_video-captioning_base_en](https://www.modelscope.cn/models/iic/multi-modal_hitea_video-captioning_base_en) |

## 安装并运行

> [!CAUTION]
>
> ZerolanLiveRobot 2.0 版本与旧版本不兼容，因此您可能需要重新配置环境、安装依赖。

### 部署核心服务

请移步至[此处](https://github.com/AkagawaTsurunaki/zerolan-core)进完成 Zerolan Core 的相关部署工作，Zerolan Live Robot 强依赖于此核心服务。

### 安装本项目依赖

运行指令，这会安装基础环境需要的依赖包：

```shell
conda create --name ZerolanLiveRobot python=3.10
conda activate ZerolanLiveRobot
pip install -r requirements.txt
```

如果您在 `dev` 开发分支，您需要安装：

```shell
pip install git+https://github.com/AkagawaTsurunaki/zerolan-ui.git@dev
pip install git+https://github.com/AkagawaTsurunaki/zerolan-data.git@dev
```

### 修改配置

找到 `resources/config.template.yaml` 配置文件，更名为 `config.yaml` ，然后根据配置文件中的注释修改为您需要的配置。

### 启动本项目

建议启动前利用 Postman 等 API 测试工具测试与 Zerolan Core 的连接是否正确。Zerolan Live Robot 会在管线连接出错时提供一些建议，仍需要您手动排查。

使用以下命令运行 Zerolan Live Robot 的主程序：

```shell
python main.py
```

### Minecraft 支持

本项目与 [KonekoMinecraftBot](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot) 共同实现了一套接口，可以从本项目控制在 Minecraft 游戏中的机器人。如有需要请移步至[此处](https://github.com/AkagawaTsurunaki/KonekoMinecraftBot)查看详细。


## API 文档

> 正在开发中……待补充

## 常见问题

### 模型服务启动失败

启动后日志显示“在其上下文中，该请求的地址无效。”。

解决方案，检查配置文件中，`host` 的配置是否正确。如果想要仅本机访问，请指定为 `'127.0.0.1'`。

## License

Feel free to enjoy open-souce!

MIT License

Copyright (c) 2024 AkagawaTsurunaki

## Contact with Me

**Email**: AkagawaTsurunaki@outlook.com

**Github**: AkagawaTsurunaki

**Bilibili**: [赤川鹤鸣_Channel](https://space.bilibili.com/1076299680)
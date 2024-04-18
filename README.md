# Zerolan Live Robot

![Static Badge](https://img.shields.io/badge/Python%20-%203.10%20-%20blue) ![Static Badge](https://img.shields.io/badge/Node%20-%2020.9.0%20-%20violet) ![Static Badge](https://img.shields.io/badge/CUDA%20-%202.1.1%2Bcu118%20-%20green) ![Static Badge](https://img.shields.io/badge/License%20-%20GPLv3%20-%20orange) 

![Static Badge](https://img.shields.io/badge/AI%20VTuber%20-%20green) ![Static Badge](https://img.shields.io/badge/Bilibli%20Live%20-%20green) ![Static Badge](https://img.shields.io/badge/Large%20Language%20Model%20-%20green) ![Static Badge](https://img.shields.io/badge/Text%20to%20Speech%20-%20green) ![Static Badge](https://img.shields.io/badge/Image%20to%20Text%20-%20green) ![Static Badge](https://img.shields.io/badge/Minecraft%20AI%20Agent%20-%20green) ![Static Badge](https://img.shields.io/badge/Automatic%20Speech%20Recognition%20%20-%20green)

*Docs Languages: [简体中文](https://github.com/AkagawaTsurunaki/ZerolanLiveRobot/blob/main/README.md) | [English](https://github.com/AkagawaTsurunaki/ZerolanLiveRobot/blob/main/docs/en/README.md) | [日本語](https://github.com/AkagawaTsurunaki/ZerolanLiveRobot/blob/main/docs/ja/README.md)*

你或许已经听说过著名的 [Neurosama](https://virtualyoutuber.fandom.com/wiki/Neuro-sama)，或者是来自中国的[木几萌](https://mobile.moegirl.org.cn/%E6%9C%A8%E5%87%A0%E8%90%8C)。 
你是否也想要拥有一个自己的 AI 虚拟形象陪你直播聊天、打游戏？
开源的 Zerolan Live Robot 正致力于实现您的梦想！而这仅仅需要一张消费级显卡！

Zerolan Live Robot 是一款多功能的直播机器人（AI VTuber），它可以自动在 Bilibili 直播间中读取弹幕，观察电脑屏幕的指定窗口，理解其画面内容，操纵 Minecraft 中的游戏角色，做出带情感的语音聊天回应。

本项目持续开发中，当前的版本为 `1.0`，您可以关注开发者的Bilibili账号[赤川鶴鳴_Channel](https://space.bilibili.com/1076299680)，正在根据此项目调教 AI 猫娘，不定时直播展示最新进展。

> 希望每个人都能拥有自己的 AI 猫娘喵！

## 目前的基本功能

1. 实时读取 Bilibili 直播间弹幕。
2. 识别并理解指定窗口的内容，例如 Minecraft。
3. 基于大语言模型 ChatGLM 3 的游戏实况聊天对话。
4. 基于 GPT-SoVITS 的语音合成，且带有语气切换功能。
4. 基于 mineflayer 的 Minecraft 智能体陪玩。

## 模型组合选择

运行本项目，您需要有支持 CUDA 的显卡。下表为您展示了一些可能的组合，请根据您的显卡的显存大小，决定使用什么模型组合。以下数据已经过开发者的直播测试（测试时还有直播姬、Minecraft Server 等程序在后台运行），仅供参考。

| 组合 | Large Language Model       | Text to Speech | Image-Text Captioning       | OBS              | Minecraft                | 显存占用 |
| ---- | -------------------------- | -------------- | --------------------------- | ---------------- | ------------------------ | -------- |
| 1    | ChatGLM3 (4-bit Quantized) | GPT-SoVTIS     | blip-image-captioning-large | 应用高质量编码器 | 1.20.4 无光影 默认材质包 | 10.9 GB  |
| 2    | ChatGLM3 (4-bit Quantized) | GPT-SoVTIS     | blip-image-captioning-large | 应用高质量编码器 | -                        | 9.3 GB   |
| 3    | ChatGLM3 (4-bit Quantized) | GPT-SoVTIS     | blip-image-captioning-large | -                | -                        | 8.8 GB   |
| 4    | ChatGLM3 (4-bit Quantized) | GPT-SoVTIS     | -                           | -                | -                        | 7.7 GB   |
| 5    | ChatGLM3 (4-bit Quantized) | -              | -                           | -                | -                        | 5.4 GB   |

*注：这里的 ChatGLM3 是指参数量为 6B 的模型。*

开发者测试时的电脑配置如下，仅供参考。

| 设别名称 | 设备型号                       | 补充说明   |
| -------- | ------------------------------ | ---------- |
| Windows  | Windows 11                     | -          |
| CPU      | i9-13900HX                     | 24 内核    |
| GPU      | NVIDIA GeForce RTX 4080 Laptop | 12 GB 显存 |
| 内存     | -                              | 32 GB 内存 |

此外您还需注意：

1. 多个程序同时抢占 GPU 资源可能导致服务响应中断。例如，OBS 在进行解码时对 GPU 的占用显著提高，从而导致 LLM 或 TTS 服务被操作系统挂起。
2. 项目运行时可能会持续消耗显卡资源，请注意散热，避免引发火灾风险。
3. 上述数据在不同系统和硬件上可能存在差异，请注意留足冗余量。
4. 本项目尚不支持多卡运行，如果有需要您可以自行更改代码。

## 准备工作

我们假定您已经正确地安装了 Anaconda 和 Python。

### 克隆仓库

确保您已经正确安装了 Git，然后执行以下指令，它将克隆本仓库到您的本机。

```shell
git clone https://github.com/AkagawaTsurunaki/ZerolanLiveRobot.git
```

### 安装依赖

首先，让我们使用 Anaconda 创建一个虚拟环境。

```shell
conda create --name zerolanliverobot python=3.10 -y # 创建虚拟环境
```

这将命令 Anaconda 创建一个名为`zerolanliverobot`的虚拟环境，且指定了 Python 版本为 3.10。

```shell
cd YourDirectory/ZerolanLiveRobot # 切换目录至本仓库的目录
conda activate zerolanliverobot # 激活刚刚创建的虚拟环境
pip install -r requirements.txt # 安装依赖
```

在这里注意的是，本项目中的依赖 `torch~=2.1.1+cu118` 可能因为您的 CUDA 设备具有不同的驱动版本而在安装时报错，如果报错请切换至对应的版本。

要运行 Minecraft AI Agent，您还需要安装 Node.js 20.9.0，并执行以下指令。

```shell
cd YourDirectory/ZerolanLiveRobot # 切换目录至本仓库的目录
npm install # 安装必要依赖
```

这会下载必要的依赖。

### 下载必要模型

| 模型名称                                                     | 下载与安装方式                                               | 用途       |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ---------- |
| [ChatGLM3](https://github.com/THUDM/ChatGLM3)                | `git clone https://huggingface.co/THUDM/chatglm3-6b`         | 大语言模型 |
| [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)         | 请仔细阅读[这里](https://github.com/RVC-Boss/GPT-SoVITS)。   | 文字转语音 |
| [blip-image-captioning-large](https://huggingface.co/Salesforce/blip-image-captioning-large) | `git clone https://huggingface.co/Salesforce/blip-image-captioning-large` | 图片转文字 |

您需要自行下载模型，并且放置在一个合适的位置。在某些国家或地区，访问 Hugging Face 可能存在困难，请自行搜寻解决方案，通常您可以选择一个值得信赖的镜像网站或代理来解决。

### 修改配置

您需要找到并修改本项目中的配置文件`config/template_config.yaml`，并将`template_config.yaml`更名为`global_config.yaml`。

接下来，我们将会详细介绍配置文件中的每块内容。

#### Bilibli 直播服务

这项配置用于连接至 Bilibili 服务器，并登录您的账号，获取指定直播间的内容。

```yaml
# Bilibili 直播配置
bilibili_live_config:
  # 获取方式[详见](https://nemo2011.github.io/bilibili-api/#/get-credential)
  sessdata:
  bili_jct:
  buvid3:
  # 直播间 ID （应为数字）
  room_id:
```

其中，
1. `sessdata`、`bili_jct`、`buvid3` 这三项用于向 Bilibili 服务器校验您的身份，如果不登录将无法获取直播间的弹幕信息。具体如何填写这三个值，详见[此处](https://nemo2011.github.io/bilibili-api/#/get-credential)。请注意，不要将这三项泄露给他人，尤其在直播的时候，这将会有盗号风险。
2. `room_id` 是您要连接的直播间的ID，通常为直播间URL中的从左到右第一次出现的数字。当然，您可以设置为他人直播间的ID，这样会接受他人直播间的弹幕信息。

#### 截屏服务

这一部分是为了让 ZEROLAN LIVE ROBOT 可以识别当前画面中的的实时内容，你可以指定ta可以看到的窗口，例如游戏画面。

```yaml
# 截屏配置
screenshot_config:
  # 窗口标题（会自动查找符合该标题的第一个窗口）
  win_title:
  # 缩放因子（为了防止屏幕被截取窗口）
  k: 0.9
  # 截取的图片存放位置
  save_dir: .tmp/screenshots
```

其中，
1. `win_title` 代表要识别的窗口标题，您也可以不填全，这样会在自动匹配的窗口列表中选择第一个窗口进行观测。
2. `k` 缩放因子，它的作用是防止窗口的边框和标题栏被识别到，从而使 AI 失去沉浸感。取值越小，AI 可识别的范围越小，取值 0 ~ 1 之间。
3. `save_dir` 截取的图片存放目录，会保存为若干个`时间戳.png`这样的图片。程序停止不会自动清除这里的图片。

#### 视觉识别服务

我们使用 [blip-image-captioning-large]([Salesforce/blip-image-captioning-large · Hugging Face](https://huggingface.co/Salesforce/blip-image-captioning-large)) 这一模型以完成 Image-to-Text 任务，这里要注意的是，这个模型输出的是**英文**。

关于配置文件，

```yaml
# 模型 blip-image-captioning-large 的配置
blip_image_captioning_large_config:
  # 模型地址
  model_path: Salesforce/blip-image-captioning-large
  # 模型默认文本提示词（只能是英文）
  text_prompt: There
```

其中，

1. `model_path` 表示模型的存放位置。
2. `text_prompt` 表示模型的文本提示词（必须是英文），例如当你使用`There `时，模型的输出就会以`There`开头。

#### 配置并启动 GPT-SoVITS 服务

关于本项目采用的 TTS 模型[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)，这是一个可以支持仅需3到10秒的音频克隆的模型。请移步至官方仓库，了解如何下载并使用该模型。

关于 GPT-SoVITS 官方的 API 如何支持中英、日英混读，请参考如下的[教程](https://github.com/jianchang512/gptsovits-api)修改。

请按照上述仓库中文档中的操作步骤配置 GPT-SoVITS 服务，并启动 API 服务，也请记住您的 API 服务的相关配置。

```yaml
GPTSoVITSServiceConfig:
  # 是否以调试模式运行
  debug: False
  # GPT-SoVITS 服务地址
  host: 127.0.0.1
  # GPT-SoVITS 服务端口
  port: 9880
  # 音频临时文件夹
  tmp_dir: .tmp/wav_output
```

其中，

1. `debug`：是否以调试模式启动Flask服务，默认为`False`。

2. `host`：GPT-SoVITS 服务地址，如果您在本机上启动，那么默认地址为`127.0.0.1`。

3. `prot`：GPT-SoVITS 服务端口，如果您未进行改动，那么默认端口为`9880`。

4. `tmp_dir`用于临时存放生成的音频文件，您可以选择一个合适的位置，默认为`.tmp/wav_output`。

#### 语气分析服务配置

为了能让虚拟形象以不同的语气说话，您需要在 `template/tone_list.yaml` 配置中修改自定义的Prompt。以下是一个示例。

```yaml
EMOTION_ID:
  refer_wav_path: 1.wav
  prompt_text: 你好，请多关照。
  prompt_language: zh
```

其中，

1. `EMOTION_ID` 表示此 Prompt 所包含的语气，例如“`开心`”、“`生气`”。请注意，根据您使用的大语言模型所支持的语言，来设定`EMOTION_ID`的效果可能会更好。
2. `refer_wav_path`：此 Prompt 音频文件的路径。注意音频的**长度必须大于 3 秒但小于 10 秒**。
3. `prompt_text`：此 Prompt 音频文件中表述的内容。
4. `prompt_language`：此此 Prompt 音频所用的语言。GPT-SoVITS 目前仅支持`zh`（中文）、`en`（英语）、`ja`（日语）这三国语言。

#### ChatGLM3 服务配置

[ChatGLM3](https://github.com/THUDM/ChatGLM3)是本项目的核心，如果您无法正确启动此服务，那么将无法启动本项目。以下是配置文件：

```yaml
# ChatGLM3 服务配置
chatglm3_service_config:
  # 是否以调试模式运行
  debug: False
  # ChatGLM3 服务地址
  host: 127.0.0.1
  # ChatGLM3 服务端口
  port: 8085
  # Tokenizer 路径
  tokenizer_path: THUDM/chatglm3-6b
  # 模型路径
  model_path: THUDM/chatglm3-6b
  # 量化
  quantize: 4
```

其中，

1. `debug`：参数用来指定 Flask 是否以 debug 模式启动，默认为 `Flase`。
2. `host`：ChatGLM 服务地址，如果您在本机上启动，那么默认地址为`127.0.0.1`。
3. `port`：ChatGLM 服务端口，如果您未进行改动，那么默认端口为`8085`。
4. `tokenizer_path`：ChatGLM 模型目录。
5. `model_path`：ChatGLM 分词器目录，通常和 `tokenizer_path` 一样。
6. `quantize`：ChatGLM 的量化等级，通常为 4，如果您的显存足够支持更大的量化等级，可以使用 8。

#### OBS 服务配置

[OBS](https://obsproject.com/download) 是一款免费且开源的视频录制和直播软件。以下的配置文件主要是为了您能够显示相关字幕。当然，如果不需要直播等功能，您也可以不使用此配置文件。

```yaml
# OBS 服务配置
obs_config:
  # 弹幕输出字幕文件
  danmaku_output_path: .tmp/danmaku_output/output.txt
  # 语气输出字幕文件
  tone_output_path: .tmp/tone_output/output.txt
  # 大语言模型输出字幕文件
  llm_output_path: .tmp/llm_output/output.txt
```

其中，

1. `danmaku_output_path`：被选择读取到的弹幕会被输出到这个路径的文件中。
2. `tone_output_path`：模型输出的语气会被输出到这个路径的文件中。
3. `llm_output_path`：模型输出的文字会被输出到这个路径的文件中。

#### Zerolan 配置

这是针对本项目的配置文件。

```yaml
# 本项目配置
zerolan_live_robot_config:
  # 提示词模板
  custom_prompt_path: template/custom_prompt.yaml
```

提示词模板 `custom_prompt.json` 中的内容举例如下：

```json
{
  "query": "",
  "history": [
    {
      "content": "你现在是一只猫娘，无论说什么都要带喵字。记住了的话，只需要回复：好的主人喵！",
      "metadata": "",
      "role": "user"
    },
    {
      "content": "好的主人喵！",
      "metadata": "",
      "role": "assistant"
    },
    {
      "content": "现在你是什么？",
      "metadata": "",
      "role": "user"
    },
    {
      "content": "主人，我是一只猫娘喵！",
      "metadata": "",
      "role": "assistant"
    }
  ],
  "temperature": 1,
  "top_p": 1
}
```

其中，`history` 列表中可以填入若干轮对话，可以按照您自己的需求进行修改和扩充。这里的 `role` 属性中，`user` 代表用户的输入，而 `assistant` 表示模型输出。

## 开始运行

首先，启动 ChatGLM3 服务。

```shell
cd YourDirectory/ZerolanLiveRobot # 切换目录至本仓库的目录
conda activate zerolanliverobot # 激活刚刚创建的虚拟环境
python api_run.py # 启动大语言模型 ChatGLM3
```

大语言模型需要一段时间去加载，请耐心等待。

接着，启动 GPT-SoVTIS 服务。启动脚本请遵循 GPT-SoVTIS 原项目的文档要求进行设置。

确保 ChatGLM3 和 GPT-SoVTIS 均被正确启动后，您可以运行以下代码来运行本项目。

```shell
cd YourDirectory/ZerolanLiveRobot # 切换目录至本仓库的目录
conda activate zerolanliverobot # 激活刚刚创建的虚拟环境
python main.py # 启动主程序
```

如果一切正常，稍后就能听到合成的语音被自动播放了（注意系统音量，不要损伤您的听力）。

如果您需要开启 Minecraft AI Agent 与您一同在服务器中游玩，可以使用以下命令。

```shell
node minecraft/service.js host port username password
```

其中，

1. `host`：Minecraft 服务器的地址，如果您在本机开启了服务器，请使用 `127.0.0.1`。
2. `port`：Minecraft 服务器的端口，如果您没有修改默认的端口号，那么通常为 `25565`。
3. `username`：Minecraft AI Agent 将要登入的服务器的玩家名称，在游戏中将以此名称显示。
4. `password`：Minecraft AI Agent 将要登入的服务器的密码，如果没有设置密码，请忽略这个字段。

## 常见问题

#### GPT-SoVTIS 服务无法连接

```
CRITICAL | gptsovits.service:init:26 - ❌️ GPT-SoVTIS 服务无法连接至 http://127.0.0.1:9880
```

出现这种情况，是因为程序无法访问这个地址 `http://127.0.0.1:9880`（根据您的配置不同可能略有差异），请检查您在 GPT-SoVITS 项目中是否正确启动了 api 服务。注意您应该启动的是 `api.py` 或者 `api2.py` 而不是启动  `webui.py`。

#### 无法找到窗口

```
WARNING  | scrnshot.service:screen_cap:32 - 无法找到窗口 xxx
```

如字面意思，程序无法找到您在配置文件中设置的 `screenshot_config.win_title` 所指定的窗口。请检查您对应的窗口确实开启了，或者是否存在拼写错误。

## 开源许可证

本项目使用“GNU通用公共许可证”（GNU GENERAL PUBLIC LICENSE，GPLv3），我们希望以自由的方式使用户从本项目中受益。

## 特别鸣谢

本项目用到了以下开源项目的部分或全部的技术，再此特别感谢开源社区为人类社会的贡献。

[THUDM/ChatGLM3: ChatGLM3 series: Open Bilingual Chat LLMs | 开源双语对话语言模型 (github.com)](https://github.com/THUDM/ChatGLM3)

[RVC-Boss/GPT-SoVITS: 1 min voice data can also be used to train a good TTS model! (few shot voice cloning) (github.com)](https://github.com/RVC-Boss/GPT-SoVITS)

[Salesforce/blip-image-captioning-large · Hugging Face](https://huggingface.co/Salesforce/blip-image-captioning-large)

[Nemo2011/bilibili-api: 哔哩哔哩常用API调用。支持视频、番剧、用户、频道、音频等功能。原仓库地址：https://github.com/MoyuScript/bilibili-api](https://github.com/Nemo2011/bilibili-api)

[PrismarineJS/mineflayer: Create Minecraft bots with a powerful, stable, and high level JavaScript API. (github.com)](https://github.com/PrismarineJS/mineflayer)

此处可能未能详尽展示，如有疏漏，可以联系开发者。

## 联系方式

如果您对本项目有何建议或问题等，可以通过以下联系方式与开发者交流。

邮箱：AkagawaTsurunaki@outlook.com

QQ群：858378209

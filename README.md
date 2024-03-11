# ZEROLAN LIVE ROBOT

| AI 虚拟主播 | 直播机器人 | 大语言模型 | 文本转语音 | 图像识别 |

ZEROLAN LIVE ROBOT 可以自动在 Bilibili 直播间中读取弹幕，同时观察屏幕指定窗口，理解其画面内容，通过大语言模型的推理和文本转语音技术做出回应。
后续可能会添加更多的功能，例如LIVE2D控制、打游戏等。

本项目持续开发中，您可以关注Bilibili账号[赤川鶴鳴_Channel](https://space.bilibili.com/1076299680]) ，正在调教猫娘，不定时直播展示最新进展。

Python >= 3.10

## 基本功能

1. 实时读取 Bilibili 直播间弹幕。
2. 识别并理解 Windows 中指定窗口的内容。
3. 基于大语言模型的游戏实况聊天对话。
4. 基于语句语气的自调整的情感语音合成。

## 模型组合选择

运行本项目，您需要有支持 CUDA 的显卡。下表为您展示了一些可能的组合，请根据您的显卡的显存大小，决定使用什么模型组合。

| 组合 | Large Language Model       | Text to Speech | Image-Text Captioning       | 显存占用    |
|----|----------------------------|----------------|-----------------------------|---------|
| 1  | ChatGLM3 (4-bit Quantized) | GPT-SoVTIS     | blip-image-captioning-large | 10.1 GB |
|    |                            |                |                             |         |

请注意，如果您需要运行别的软件，例如 OBS 或者原神，则必须考虑到即使显存没有占满，
显存的有限算力可能也会因为多个应用的抢占，从而导致项目的运行延迟增大。

本项目在 NVIDIA GeForce RTX 4080 Laptop （拥有12GB的显存）上运行良好。

## 准备工作

您需要找到并修改本项目中的配置文件`config/template_config.yaml`，
并将`template_config.yaml`更名为`global_config.yaml`。
接下来，我们将会详细介绍配置文件中的每块内容。

### Bilibli 直播服务

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

### 截屏服务

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

```yaml
# 模型 blip-image-captioning-large 的配置
blip_image_captioning_large_config:
  # 模型地址
  model_path: Salesforce/blip-image-captioning-large
  # 模型默认文本提示词（只能是英文）
  text_prompt: There
```

### 配置并启动 GPT-SoVITS 服务

关于本项目采用的 TTS 模型
[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)，这是一个可以支持仅需3到10秒的音频克隆的模型。
请移步至官方仓库，了解如何下载并使用该模型。

关于 GPT-SoVITS 官方的 API 如何支持中英、日英混读，请参考如下的[教程](https://github.com/jianchang512/gptsovits-api)修改。

请按照上述仓库中文档中的操作步骤配置 GPT-SoVITS 服务，并启动 API 服务。

请记住您的 API 服务的相关配置，

```yaml
GPTSoVITSServiceConfig:
  # 是否以调试模式运行
  debug: False
  # GPT-SoVITS 服务地址
  host: 127.0.0.1
  # GPT-SoVITS 服务端口
  port: 9880
  # 音频临时文件夹
  tmp_dir: gptsovits\.tmp
```

其中，

1. `debug`：是否以调试模式启动Flask服务，默认为`False`。

2. `host`：GPT-SoVITS 服务地址，如果您在本机上启动，那么默认地址为`127.0.0.1`。

3. `prot`：GPT-SoVITS 服务端口，如果您未进行改动，那么默认端口为`9880`。

4. `tmp_dir`用于临时存放生成的音频文件，您可以选择一个合适的位置，默认为`gptsovits\.tmp`。

### 语气配置

为了能让虚拟形象以不同的语气说话，您需要在 `gptsovits/prompts/default.yaml` 配置中修改自定义的Prompt。
以下是一个示例。

```yaml
EMOTION_ID:
  refer_wav_path: 1.wav
  prompt_text: 你好，请多关照。
  prompt_language: zh
```

其中，

1. `EMOTION_ID` 表示此 Prompt 所包含的语气，例如“`开心`”。请注意，根据您使用的大语言模型所支持的语言，来设定`EMOTION_ID`
   的效果可能会更好。
2. `refer_wav_path`：此 Prompt 音频文件的路径。注意音频的长度必须大于 3 秒但小于 10 秒。
3. `prompt_text`：此 Prompt 音频文件中表述的内容。
4. `prompt_language`：此此 Prompt 音频所用的语言。目前仅支持`zh`（中文）、`en`（英语）、`ja`（日语）这三国语言。

## 大语言模型（LLM）

现在我们支持 [ChatGLM3](https://github.com/THUDM/ChatGLM3).

### ChatGLM3

首先，你应该使用`/config` 配置LLM服务。
这将会返回一个带有`code`的HttpResponseBody，如果值为`Code.OK`，请调用`/start`以启动服务；
否则，请根据返回的信息查看配置文件是否出现错误。

# ZEROLAN LIVE ROBOT
| AI 虚拟主播 | 直播机器人 | LLM | TTS |

ZEROLAN LIVE ROBOT 可以自动在直播间中读取弹幕，并通过大语言模型的推理和文本转语音技术做出回应。
后续可能会添加更多的功能，例如LIVE2D控制、图像识别、打游戏等。

让我们把真正的虚拟主播带到这个世界上来吧！开源拯救世界。

本项目持续开发中，您可以关注Bilibili账号[赤川鶴鳴_Channel](https://space.bilibili.com/1076299680]) ，不定时直播展示最新进展。

## 现有功能

1. 实时读取直播间弹幕
2. 大语言模型推理
3. 基于情感的语音合成

## 模型组合选择

运行本项目，您需要有支持 CUDA 的显卡。下表为您展示了一些可能的组合，请根据您的显卡的显存大小，决定使用什么模型组合。

| 组合 | LLM                        | TTS        | 显存占用   |
|----|----------------------------|------------|--------|
| 1  | ChatGLM3 (4-bit Quantized) | GPT-SoVTIS | 8.1 GB |
| 2  | ChatGLM3 (4-bit Quantized) | VALL-E X   | 7.1 GB |

请注意，如果您需要运行别的软件，例如 OBS，或者大型游戏，则必须考虑到即使显存没有占满，显存的有限算力可能也会因为多个应用的抢占，从而导致项目的运行延迟增大。

本项目在 NVIDIA GeForce RTX 4080 Laptop （拥有12GB的显存）上运行良好。

## 文本转语音（TTS）

### 配置并启动 GPT-SoVITS 服务
关于本项目采用的 TTS 模型
[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)，这是一个可以支持仅需3到10秒的音频克隆的模型。
请移步至官方仓库，了解如何下载并使用该模型。

关于 GPT-SoVITS 官方的 API 如何支持中英、日英混读，请参考如下的教程修改。
https://github.com/jianchang512/gptsovits-api

请按照上述仓库中文档中的操作步骤配置 GPT-SoVITS 服务，并启动 API 服务。

### 修改本项目中的配置文件

服务启动后，您需要修改本项目中的配置文件`gptsovits/config.yaml`。

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
  # 是否清理临时文件夹
  clean: False
```

其中，
1. `debug`：是否以调试模式启动Flask服务，默认为`False`。

2. `host`：GPT-SoVITS 服务地址，如果您在本机上启动，那么默认地址为`127.0.0.1`。

3. `prot`：GPT-SoVITS 服务端口，如果您未进行改动，那么默认端口为`9880`。

4. `tmp_dir`用于临时存放生成的音频文件，您可以选择一个合适的位置，默认为`gptsovits\.tmp`。

5. `clean`用于设置本项目启动时，是否要删除临时文件夹。为了安全起见，项目停止运行后不会立刻删除临时文件夹中的文件。但如果您将此项设置为`True`，项目启动后会进行清理，所以一定要注意不要将您需要保留的文件放在这个目录下，以免造成丢失。

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

#### Configurate the LLM service

`/config`

Request:

```json
{
  "host": "127.0.0.1",
  "port": 8721,
  "tokenizer_path": "/",
  "model_path": "/"
}
```

#### Start the LLM service

`/start`

#### Query for LLM

Request:

```json
{
  "sys_prompt": "你是一只猫娘。",
  "query": "你能叫一声吗？",
  "history": [],
  "top_p": 5,
  "temperature": 1
}
```

Response:

```json
{
  "code": 0,
  "data": {
    "history": [
      {
        "content": "你能叫一声吗？",
        "role": "user"
      },
      {
        "content": "当然可以，我在这里，请问有什么我可以帮助您的？",
        "metadata": "",
        "role": "assistant"
      }
    ],
    "response": "当然可以，我在这里，请问有什么我可以帮助您的？"
  },
  "msg": "推理成功"
}
```

Response:

#### Clear the history of LLM

`/clear`:

#### Stop the LLM service

`/stop`

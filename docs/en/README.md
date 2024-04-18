# Zerolan Live Robot

![Static Badge](https://img.shields.io/badge/Python%20-%203.10%20-%20blue) ![Static Badge](https://img.shields.io/badge/Node%20-%2020.9.0%20-%20violet) ![Static Badge](https://img.shields.io/badge/CUDA%20-%202.1.1%2Bcu118%20-%20green) ![Static Badge](https://img.shields.io/badge/License%20-%20GPLv3%20-%20orange)

![Static Badge](https://img.shields.io/badge/AI%20VTuber%20-%20green) ![Static Badge](https://img.shields.io/badge/Bilibli%20Live%20-%20green) ![Static Badge](https://img.shields.io/badge/Large%20Language%20Model%20-%20green) ![Static Badge](https://img.shields.io/badge/Text%20to%20Speech%20-%20green) ![Static Badge](https://img.shields.io/badge/Image%20to%20Text%20-%20green) ![Static Badge](https://img.shields.io/badge/Minecraft%20AI%20Agent%20-%20green) ![Static Badge](https://img.shields.io/badge/Automatic%20Speech%20Recognition%20%20-%20green)

*Docs Languages: [简体中文](https://github.com/AkagawaTsurunaki/ZerolanLiveRobot/blob/main/README.md) | [English](https://github.com/AkagawaTsurunaki/ZerolanLiveRobot/blob/main/docs/en/README.md) | [日本語](https://github.com/AkagawaTsurunaki/ZerolanLiveRobot/blob/main/docs/ja/README.md)*

You may have heard of the famous [Neurosama](https://virtualyoutuber.fandom.com/wiki/Neuro-sama),
or [Mu Jimeng](https://mobile.moegirl.org.cn/%E6%9C%A8%E5%87%A0%E8%90%8C) from China. Do you also want to have your own
AI avatar to accompany you live chat, play games? The open source Zerolan Live Robot is committed to making your dreams
come true! And what you need is a consumer GPU!

Zerolan Live Robot is a multifunctional live streaming robot (AI VTuber) that automatically reads a barrage in the
Bilibili studio, looks at specific windows on the computer screen to understands its content, and manipulates Minecraft
characters, with making emotional voice chat responses.

This project is under continuous development, and the current version is `1.0`. You can follow the developer's Bilibili
account [赤川鶴鳴_Channel](https://space.bilibili.com/1076299680), who is training AI Neko Musume according to this
project and will show the latest progress in the live room.

> Hope everyone can have their own AI cat cat!

## Current Basic Functionalities

1. Real-time reading of the Bilibili live room danmaku.
2. Recognize and understand the contents of a specified window, such as Minecraft.
3. Live game chat dialogue based on large language model ChatGLM 3.
4. Speech synthesis based on GPT-SoVITS with tone switching function.
5. Minecraft AI Agent based on mineflayer.

## Model Combination Selection

To run this project, you need to have a CUDA-enabled GPU. The following table shows you some possible combinations,
depending on the memory size of your GPU, decide which model combination to use. The following data has been tested by
the developer during the live (there are also Zhiboji, Minecraft Server and other programs running in the background
during the test), for reference only.

| Comb. | Large Language Model       | Text to Speech | Image-Text Captioning       | OBS                   | Minecraft                                  | VRAM Required |
|-------|----------------------------|----------------|-----------------------------|-----------------------|--------------------------------------------|---------------|
| 1     | ChatGLM3 (4-bit Quantized) | GPT-SoVTIS     | blip-image-captioning-large | High quality encoders | 1.20.4, no shader, default resource packs. | 10.9 GB       |
| 2     | ChatGLM3 (4-bit Quantized) | GPT-SoVTIS     | blip-image-captioning-large | High quality encoders | -                                          | 9.3 GB        |
| 3     | ChatGLM3 (4-bit Quantized) | GPT-SoVTIS     | blip-image-captioning-large | -                     | -                                          | 8.8 GB        |
| 4     | ChatGLM3 (4-bit Quantized) | GPT-SoVTIS     | -                           | -                     | -                                          | 7.7 GB        |
| 5     | ChatGLM3 (4-bit Quantized) | -              | -                           | -                     | -                                          | 5.4 GB        |

*Note: ChatGLM3 here refers to a model with a parameter count of 6B.*

The developer's computer configuration for testing is as follows for reference only.

| Device Name |                                | Additional Information |
|-------------|--------------------------------|------------------------|
| Windows     | Windows 11                     | -                      |
| CPU         | i9-13900HX                     | 24 Cores               |
| GPU         | NVIDIA GeForce RTX 4080 Laptop | 12 GB VRAM             |
| Memory      | -                              | 32 GB RAM              |

In addition, you should note:

1. If multiple programs preempt GPU resources at the same time, service response may be interrupted. For example, OBS
   significantly increases the GPU footprint when decoding, resulting in LLM or TTS service suspended by your OS.
2. GPU resources may continue to be consumed when the project is running. Please pay attention to heat dissipation to
   avoid fire risk.
3. The preceding data may vary depending on the system and hardware. Ensure sufficient redundancy.
4. This project does not support multi-card operation, you can change the code yourself if necessary.

## Preparation

We assume that you have installed Anaconda and Python correctly.

### Clone Repository

Make sure you have Git installed correctly, and then execute the following command, which will clone the repository to
your local machine.

```shell
git clone https://github.com/AkagawaTsurunaki/ZerolanLiveRobot.git
```

### Install Dependencies

First, let's create a virtual environment using Anaconda.

```shell
conda create --name zerolanliverobot python=3.10 -y # Create virtual environment
```

This commands Anaconda to create a virtual environment called `zerolanliverobot`, specifying Python version 3.10.

```shell
cd YourDirectory/ZerolanLiveRobot # Change directory to the directory of this repository
conda activate zerolanliverobot # Activate the virtual environment just created
pip install -r requirements.txt # Install dependencies
```

Note here that the dependency `torch~=2.1.1+cu118` in this project may be incorrectly installed because your CUDA device
has a different driver version. If an error occurs, please switch to the corresponding version.

To run the Minecraft AI Agent, you need to install Node.js 20.9.0 and execute the following commands:

```shell
cd YourDirectory/ZerolanLiveRobot # Change directory to the directory of this repository
npm install # Install necessary dependencies
```

This will download the required dependencies.

### Download Required Models

| Model Name                                                                                   | Download and Installation Method                                          | Purpose       |
|----------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|---------------|
| [ChatGLM3](https://github.com/THUDM/ChatGLM3)                                                | `git clone https://huggingface.co/THUDM/chatglm3-6b`                      | LLM           |
| [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)                                         | Please refer to [this link](https://github.com/RVC-Boss/GPT-SoVITS).      | TTS           |
| [blip-image-captioning-large](https://huggingface.co/Salesforce/blip-image-captioning-large) | `git clone https://huggingface.co/Salesforce/blip-image-captioning-large` | Image-to-Text |

You need to download the models yourself and place them in suitable locations. In some countries or regions, visit
Hugging Face
There may be difficulties, please search for a solution on your own, usually you can choose a trusted mirror site or
proxy to solve.

### Modify Configuration

You need to locate and modify the configuration file `config/template_config.yaml` in this project and
rename `template_config.yaml` to `global_config.yaml`.

Next, we'll look at each item in the configuration file in detail.

#### Bilibili Live Service

This configuration is used to connect to the Bilibili server, log in to your account, and retrieve content from the
specified live broadcast room.

```yaml
# Bilibili Live Service
bilibili_live_config:
  # How to get these attributes, please [see](https://nemo2011.github.io/bilibili-api/#/get-credential).
  sessdata:
  bili_jct:
  buvid3:
  # Live room ID (number required)
  room_id:
```

In this context,

1. The three items `sessdata`, `bili_jct` and `buvid3` are used to send information to Bilibili.
   The server verifies your identity, and if you do not log in, you will not be able to get the danmaku information from
   your live room. Specific how to fill in these three values,
   see [here](https://nemo2011.github.io/bilibili-api/#/get-credential).
   Please be careful not to disclose these three items to others, especially during live broadcasting, which will lead
   to the risk of theft.

2. `room_id` is the ID of the live room you want to connect to, usually the number that first appears from left to right
   in the URL of your live room. Of course, you can set the ID of someone else's live room, so that you will accept the
   danmaku information of others' live room.

#### Screenshot Service

This part is so that Zerolan Live Robot can recognize the live content in your current screen, you can specify the
window that the robot can see, such as the game screen.

```yaml
# Screenshot configuration
screenshot_config:
  # Window title (automatically finds the first window that matches the title)
  win_title:
  # Scaling factor (to prevent screen capture of window's bar)
  k: 0.9
  # Location of the captured image
  save_dir: .tmp/screenshots
```

In this context,

1. `win_title` represents the title of the window to be recognized, you can also leave it uncompleted, so that the first
   window will be selected in the list of automatically matched Windows for capturing.
2. `k` scaling factor, its role is to prevent the window's border and title bar from being recognized, so that the AI
   loses immersion. The smaller the value, the smaller the range that the AI can identify. The value ranges from 0 to 1.
3. `save_dir` captured pictures stored in the directory, will be saved as named file like `timestamped.png`. Stopping
   the program will not automatically clear the images here.

#### Visual Recognition Service

We use the [blip-image-captioning-large](https://huggingface.co/Salesforce/blip-image-captioning-large) model to perform
the Image-to-Text task. It is important to note that the output of this model is in **English**.

Regarding the configuration file,

```yaml
# Configuration for the blip-image-captioning-large model
blip_image_captioning_large_config:
  # Model path
  model_path: Salesforce/blip-image-captioning-large
  # Default text prompt for the model (must be in English)
  text_prompt: There
```

In this context,

1. `model_path` indicates the location of the model.
2. `text_prompt` represents the model's text prompt (must be in English). For example, when you use `There` , the
   model's output will start with `There`.

#### Configure and Start the GPT-SoVITS Service

For information about the TTS model [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) used in this project, which is
a model capable of cloning audio within just 3 to 10 seconds, please visit the official repository to learn how to
download and utilize the model.

Regarding how the official API of GPT-SoVITS supports mixed Chinese-English and Japanese-English reading, please refer
to the following [tutorial](https://github.com/jianchang512/gptsovits-api) for modifications.

Follow the steps outlined in the documentation of the repository to configure the GPT-SoVITS service and start the API
service, and remember the relevant configurations of your API service.

```yaml
GPTSoVITSServiceConfig:
  # Whether to run in debug mode
  debug: False
  # GPT-SoVITS service address
  host: 127.0.0.1
  # GPT-SoVITS service port
  port: 9880
  # Temporary folder for audio files
  tmp_dir: .tmp/wav_output
```

In this context,

1. `debug`: Whether to start the Flask service in debug mode, default is `False`.
2. `host`: GPT-SoVITS service address. If you are running it on your local machine, the default address is `127.0.0.1`.
3. `port`: GPT-SoVITS service port. If you haven't made any changes, the default port is `9880`.
4. `tmp_dir`: Used to temporarily store the generated audio files. You can choose a suitable location, with the default
   being `.tmp/wav_output`.

#### Tone Analysis Service Configuration

To enable the virtual avatar to speak in different tones, you need to modify custom prompts in
the `template/tone_list.yaml` configuration. Here is an example:

```yaml
EMOTION_ID:
  refer_wav_path: 1.wav
  prompt_text: Hello, nice to meet you.
  prompt_language: en
```

In this context,

1. `EMOTION_ID`: Represents the tone contained in this prompt, such as "`happy`" or "`angry`". Please note that
   setting `EMOTION_ID` based on the language supported by the LLM you are using may yield better results.
2. `refer_wav_path`: Path to the audio file for this prompt. Note that the audio must be **longer than 3 seconds but
   less than 10 seconds**.
3. `prompt_text`: The content expressed in the audio file for this prompt.
4. `prompt_language`: The language used in the audio for this prompt. GPT-SoVITS currently supports only three
   languages: `zh` (Chinese), `en` (English), and `ja` (Japanese).

#### ChatGLM3 Service Configuration

[ChatGLM3](https://github.com/THUDM/ChatGLM3) is the core of this project. If you fail to start this service correctly,
the project will not be able to launch. Below is the configuration file:

```yaml
# ChatGLM3 Service Configuration
chatglm3_service_config:
  # Run in debug mode or not
  debug: False
  # ChatGLM3 service host
  host: 127.0.0.1
  # ChatGLM3 service port
  port: 8085
  # Tokenizer path
  tokenizer_path: THUDM/chatglm3-6b
  # Model path
  model_path: THUDM/chatglm3-6b
  # Quantization level
  quantize: 4
```

Where,

1. `debug`: Specifies whether Flask runs in debug mode, default is `False`.
2. `host`: The host address of the ChatGLM service. If you are running it on your local machine, the default address
   is `127.0.0.1`.
3. `port`: The port of the ChatGLM service. If unchanged, the default port is `8085`.
4. `tokenizer_path`: The directory of the ChatGLM model.
5. `model_path`: The directory of the tokenizer used by ChatGLM, usually the same as `tokenizer_path`.
6. `quantize`: The quantization level of ChatGLM, typically set to 4. If your GPU memory can support a higher
   quantization level, you can use 8.

#### OBS Service Configuration

[OBS](https://obsproject.com/download)  is a free and open-source software for video recording and live streaming. The
following configuration file is primarily for displaying subtitles. Of course, if you do not need live streaming
functionality, you can choose not to use this configuration file.

```yaml
# OBS Service Configuration
obs_config:
  # Danmaku output subtitle file
  danmaku_output_path: .tmp/danmaku_output/output.txt
  # Tone output subtitle file
  tone_output_path: .tmp/tone_output/output.txt
  # Large Language Model (LLM) output subtitle file
  llm_output_path: .tmp/llm_output/output.txt
```

Where,

1. `danmaku_output_path`: Selected danmaku will be output to the file located at this path.
2. `tone_output_path`: Model-generated tones will be output to the file located at this path.
3. `llm_output_path`: Model-generated text will be output to the file located at this path.

#### Zerolan Configuration

This is the configuration file for this project.

```yaml
# Project Configuration
zerolan_live_robot_config:
  # Prompt Template
  custom_prompt_path: template/custom_prompt.yaml
```

The contents of the prompt template `custom_prompt.json` are as follows:

```json
{
  "query": "",
  "history": [
    {
      "content": "You are now a Neko Musume, and you must include 'meow' in everything you say. Remember this: 'Yes, my master, meow!'",
      "metadata": "",
      "role": "user"
    },
    {
      "content": "Yes, my master, meow!",
      "metadata": "",
      "role": "assistant"
    },
    {
      "content": "What are you now?",
      "metadata": "",
      "role": "user"
    },
    {
      "content": "Master, I am a Neko Musume, meow!",
      "metadata": "",
      "role": "assistant"
    }
  ],
  "temperature": 1,
  "top_p": 1
}
```

In the `history` list, you can add several dialogue turns according to your own needs. The `role` attribute in this
context, where `user` represents the user's input and `assistant` indicates the model's output.

## Getting Started

First, start the ChatGLM3 service.

```shell
cd YourDirectory/ZerolanLiveRobot # Change directory to the repository folder
conda activate zerolanliverobot # Activate the virtual environment
python api_run.py # Start the ChatGLM3 language model
```

LLM may take some time to load, so please be patient.

Next, start the GPT-SoVTIS service. Follow the setup instructions of the original GPT-SoVTIS project for starting the
script.

Once both ChatGLM3 and GPT-SoVTIS are running correctly, you can execute the following code to run this project.

```shell
cd YourDirectory/ZerolanLiveRobot # Change directory to the repository folder
conda activate zerolanliverobot # Activate the virtual environment
python main.py # Start the main program
```

If everything is set up correctly, you should soon hear the synthesized speech being automatically played (adjust your
system volume to protect your hearing).

If you want to enable the Minecraft AI Agent to play on a server with you, you can use the following command.

```shell
node minecraft/service.js host port username password
```

Where:

1. `host`: The address of the Minecraft server. If you are running the server on your local machine, please
   use `127.0.0.1`.
2. `port`: The port of the Minecraft server. If you haven't changed the default port, it's usually `25565`.
3. `username`: The player name that the Minecraft AI Agent will use to log into the server and display in-game.
4. `password`: The password for the Minecraft AI Agent to log into the server. If no password is set, you can ignore
   this field.

## FAQ

#### Unable to Connect to GPT-SoVTIS Service

```
CRITICAL | gptsovits.service:init:26 - ❌️ GPT-SoVTIS 服务无法连接至 http://127.0.0.1:9880
```

If you encounter this issue, it means that the program cannot access the address `http://127.0.0.1:9880` (may vary based
on your configuration). Please check whether you have correctly started the API service in the GPT-SoVITS project. Note
that you should start `api.py` or `api2.py` instead of webui.py.

#### Window Not Found

```
WARNING  | scrnshot.service:screen_cap:32 - 无法找到窗口 xxx
```

As the message suggests, the program is unable to find the window specified by `screenshot_config.win_title` in your configuration file. Please check if the corresponding window is indeed open or if there is a spelling error.

## Open Source License

This project is licensed under the GNU General Public License (GPLv3), and we aim to provide users with the freedom to benefit from this project in a free manner.

## Special Thanks

This project utilizes some or all of the technology from the following open-source projects. We would like to express our special thanks to the open-source community for their contributions to human society.

[THUDM/ChatGLM3: ChatGLM3 series: Open Bilingual Chat LLMs | 开源双语对话语言模型 (github.com)](https://github.com/THUDM/ChatGLM3)

[RVC-Boss/GPT-SoVITS: 1 min voice data can also be used to train a good TTS model! (few shot voice cloning) (github.com)](https://github.com/RVC-Boss/GPT-SoVITS)

[Salesforce/blip-image-captioning-large · Hugging Face](https://huggingface.co/Salesforce/blip-image-captioning-large)

[Nemo2011/bilibili-api: 哔哩哔哩常用API调用。支持视频、番剧、用户、频道、音频等功能。原仓库地址：https://github.com/MoyuScript/bilibili-api](https://github.com/Nemo2011/bilibili-api)

[PrismarineJS/mineflayer: Create Minecraft bots with a powerful, stable, and high level JavaScript API. (github.com)](https://github.com/PrismarineJS/mineflayer)

The list here may not be exhaustive. If there are omissions, please feel free to contact the developers.

## Contact with me

If you have any suggestions or questions regarding this project, please feel free to contact the developers using the following information:

- Email: AkagawaTsurunaki@outlook.com

- QQ Group: 858378209

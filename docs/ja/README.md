# Zerolan Live Robot

![Static Badge](https://img.shields.io/badge/Python%20-%203.10%20-%20blue) ![Static Badge](https://img.shields.io/badge/Node%20-%2020.9.0%20-%20violet) ![Static Badge](https://img.shields.io/badge/CUDA%20-%202.1.1%2Bcu118%20-%20green) ![Static Badge](https://img.shields.io/badge/License%20-%20GPLv3%20-%20orange)

![Static Badge](https://img.shields.io/badge/AI%20VTuber%20-%20green) ![Static Badge](https://img.shields.io/badge/Bilibli%20Live%20-%20green) ![Static Badge](https://img.shields.io/badge/Large%20Language%20Model%20-%20green) ![Static Badge](https://img.shields.io/badge/Text%20to%20Speech%20-%20green) ![Static Badge](https://img.shields.io/badge/Image%20to%20Text%20-%20green) ![Static Badge](https://img.shields.io/badge/Minecraft%20AI%20Agent%20-%20green) ![Static Badge](https://img.shields.io/badge/Automatic%20Speech%20Recognition%20(not%20supported)%20-%20red)

もしかしたらあなたは有名な [Neurosama](https://virtualyoutuber.fandom.com/wiki/Neuro-sama)
や中国の[木几萌](https://mobile.moegirl.org.cn/%E6%9C%A8%E5%87%A0%E8%90%8C)について聞いたことがあるかもしれません。
自分のAIバーチャルキャラクターを持ち、ライブ配信中に一緒にチャットしたりゲームをしたりしたいですか？

オープンソースのZerolan Live Robotは、その夢を実現するために取り組んでいます！ そして、それにはたった一枚の消費レベルのGPUが必要です！

Zerolan Live Robotは、多機能なライブ配信用ロボット（AI
VTuber）であり、Bilibiliのライブ配信ルームでリアルタイムに弾幕を読み取ることができ、指定されたウィンドウの内容を認識し、Minecraft内のゲームキャラクターを操作し、感情を持った音声チャット応答を行うことができます。

このプロジェクトは現在開発中で、現在のバージョンは1.0です。開発者のBilibiliアカウント「[赤川鶴鳴_Channel](https://space.bilibili.com/1076299680)
」をフォローすることで、最新の進展を不定期にライブ配信でご覧いただけます。

> 皆が自分のAIネコ娘を持てることを願っていますにゃん！

## 現在の基本機能

1. Bilibili のライブ配信ルームから弾幕をリアルタイムに読み取る。
2. 指定したウィンドウの内容を認識し理解する、例えば Minecraft。
3. 大規模言語モデル ChatGLM3 に基づくゲーム実況チャット対話。
4. GPT-SoVITS に基づく音声合成、および感情切り替え機能を備えています。
5. mineflayer に基づく Minecraft AI Agent と共に遊ぶ。

## モデル組み合わせの選択

このプロジェクトを実行するには、CUDA
をサポートする GPU
が必要です。以下の表は、いくつかの可能な組み合わせを示しており、GPUのメモリサイズに応じてどのモデル組み合わせを使用するかを決定してください。以下のデータは、開発者によるライブテスト（配信ソフトやMinecraft
Serverなどのバックグラウンドアプリケーションも同時に実行）に基づいており、参考情報として提供されています。

| 組み合わせ | Large Language Model       | Text to Speech | Image-Text Captioning       | OBS      | Minecraft                                  | 显存占用    |
|-------|----------------------------|----------------|-----------------------------|----------|--------------------------------------------|---------|
| 1     | ChatGLM3 (4-bit Quantized) | GPT-SoVTIS     | blip-image-captioning-large | 高品質エンコーダ | 1.20.4, no shader, default resource packs. | 10.9 GB |
| 2     | ChatGLM3 (4-bit Quantized) | GPT-SoVTIS     | blip-image-captioning-large | 高品質エンコーダ | -                                          | 9.3 GB  |
| 3     | ChatGLM3 (4-bit Quantized) | GPT-SoVTIS     | blip-image-captioning-large | -        | -                                          | 8.8 GB  |
| 4     | ChatGLM3 (4-bit Quantized) | GPT-SoVTIS     | -                           | -        | -                                          | 7.7 GB  |
| 5     | ChatGLM3 (4-bit Quantized) | -              | -                           | -        | -                                          | 5.4 GB  |

*注：ここでの ChatGLM3 は、パラメータ数が6Bのモデルを指します。*

開発者によるコンピューター構成は次の通りです（参考情報のみ）。

| デバイス名   | デバイスモデル                        | 追加情報       |
|---------|--------------------------------|------------|
| Windows | Windows 11                     | -          |
| CPU     | i9-13900HX                     | 24 Cores   |
| GPU     | NVIDIA GeForce RTX 4080 Laptop | 12 GB VRAM |
| 内存      | -                              | 32 GB RAM  |

その他の注意点：

1. 複数のプログラムが同時にGPUリソースを占有すると、サービスの応答が中断される可能性があります。例えば、OBSはデコード中にGPUの使用率を大幅に上昇させるため、LLMまたはTTSサービスが
   OS によって一時停止される可能性があります。
2. プロジェクト実行中には、継続的に GPU リソースを消費することがありますので、冷却に注意し、火災のリスクを回避してください。
3. 上記のデータは異なるシステムやハードウェアで異なる場合がありますので、余裕を持ってください。
4. このプロジェクトでは複数のカードの実行をサポートしていません。必要があれば、コードを自分で変更してください。

## 準備作業

Anaconda と Python が正しくインストールされていることを前提としています。

### リポジトリのクローン

Gitが正しくインストールされていることを確認した上で、以下のコマンドを実行して、このリポジトリをローカルにクローンします。

```shell
git clone https://github.com/AkagawaTsurunaki/ZerolanLiveRobot.git
```

### 依存関係のインストール

まず、Anaconda を使用して仮想環境を作成しましょう。

```shell
conda create --name zerolanliverobot python=3.10 -y # 仮想環境を作成
```

これにより、Anacondaが`zerolanliverobot`という名前の仮想環境を作成し、Python のバージョンを 3.10 に指定します。

```shell
cd YourDirectory/ZerolanLiveRobot # このリポジトリのディレクトリに移動
conda activate zerolanliverobot # 作成した仮想環境をアクティブにする
pip install -r requirements.txt # 依存関係のインストール
```

ここで注意すべき点は、このプロジェクトの依存関係である`torch~=2.1.1+cu118`
が、お使いのCUDAデバイスに異なるドライバーバージョンがある場合にインストール時にエラーが発生する可能性があるため、エラーが発生した場合は対応するバージョンに切り替えてください。

### 必要なモデルのダウンロード

| モデル名                                                                                         | ダウンロードおよびインストール方法                                                         | 用途             |
|----------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|----------------|
| [ChatGLM3](https://github.com/THUDM/ChatGLM3)                                                | `git clone https://huggingface.co/THUDM/chatglm3-6b`                      | 大規模言語モデル       |
| [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)                                         | [こちら](https://github.com/RVC-Boss/GPT-SoVITS)をよく読んでください。                  | テキスト読み上げ       |
| [blip-image-captioning-large](https://huggingface.co/Salesforce/blip-image-captioning-large) | `git clone https://huggingface.co/Salesforce/blip-image-captioning-large` | 画像テキストキャプショニング |

モデルは自分でダウンロードし、適切な場所に配置する必要があります。特定の国や地域では、Hugging
Faceへのアクセスに問題がある場合があります。問題の解決策を検索して、信頼できるミラーサイトやプロキシを選択することができます。

### 設定の変更

このプロジェクトの設定ファイル `config/template_config.yaml` を見つけて変更し、`template_config.yaml`
を `global_config.yaml` に改名してください。

次に、設定ファイルの各セクションについて詳しく説明します。

#### Bilibli ライブサービス

この設定は Bilibili サーバーに接続し、アカウントにログインして特定のライブルームのコンテンツを取得するために使用されます。

```yaml
# Bilibili ライブ設定
bilibili_live_config:
  # 取得方法[参考](https://nemo2011.github.io/bilibili-api/#/get-credential)
  sessdata:
  bili_jct:
  buvid3:
  # ライブルーム ID （数字である必要があります）
  room_id:
```

ここで、

1. `sessdata`、`bili_jct`、`buvid3` は Bilibili
   サーバーに身元を証明するために使用されます。これらの値を入力しないと、ライブルームのコメントを取得できません。これらの値の入力方法の詳細については、[こちら](https://nemo2011.github.io/bilibili-api/#/get-credential)
   を参照してください。これらの値を他人に漏洩しないように注意してください。特にライブ配信中に漏洩するとアカウントが乗っ取られるリスクがあります。
2. `room_id` は接続するライブルームのIDです。通常、URL内で最初に表示される数字です。他の人のライブルームのIDを設定することもできます。その場合、他の人のライブルームのコメントを受信します。

#### スクリーンショットサービス

この部分は Zerolan Live Robot がリアルタイムの画面内容を識別できるようにするために使用されます。ゲーム画面など、識別できるウィンドウを指定できます。

```yaml
# スクリーンショット設定
screenshot_config:
  # ウィンドウタイトル（このタイトルに一致する最初のウィンドウが自動的に選択されます）
  win_title:
  # スケーリングファクター（画面が切り取られないようにするため）
  k: 0.9
  # 切り取られた画像の保存先
  save_dir: .tmp/screenshots
```

ここで、

1. `win_title` は識別するウィンドウのタイトルを表します。部分的に入力することもでき、その場合、自動的に一致するウィンドウが選択されます。
2. `k` はスケーリングファクターで、ウィンドウの枠やタイトルバーが識別されるのを防ぎ、AI が没入感を失わないようにします。0
   から 1 の間の値を取ります。
3. `save_dir` は切り取られた画像の保存ディレクトリで、いくつかの `タイムスタンプ.png`
   形式の画像として保存されます。プログラムが停止すると、このディレクトリの画像は自動的に削除されません。

#### ビジュアル認識サービス

[blip-image-captioning-large](https://huggingface.co/Salesforce/blip-image-captioning-large) モデルを使用して
Image-to-Text タスクを完了します。
このモデルの出力は**英語**であることに注意してください。

設定ファイルに関しては、

```yaml
# モデル blip-image-captioning-large の設定
blip_image_captioning_large_config:
  # モデルパス
  model_path: Salesforce/blip-image-captioning-large
  # モデルのデフォルトテキストプロンプト（英語のみ）
  text_prompt: There
```

ここで、

1. `model_path` はモデルの保存場所を示します。
2. `text_prompt` はモデルのテキストプロンプトを示しており（英語である必要があります）、例えば `There`
   を使用すると、モデルの出力は `There` で始まります。

#### GPT-SoVITS サービスの配置と起動

このプロジェクトで使用されている TTS モデル [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
は、3〜10秒のオーディオクローンをサポートするモデルです。公式リポジトリに移動して、このモデルのダウンロードと使用方法について詳細を確認してください。

GPT-SoVITS の公式 API
がどのように中英混合読みや日英混ぜのサポートを提供しているかについては、次の[チュートリアル](https://github.com/jianchang512/gptsovits-api)
を参照してください。

上記リポジトリのドキュメントに従って、GPT-SoVITS サービスを設定し、API サービスを起動してください。また、API
サービスの関連設定を覚えておいてください。

```yaml
GPTSoVITSServiceConfig:
  # デバッグモードで実行するかどうか
  debug: False
  # GPT-SoVITS サービスのホスト
  host: 127.0.0.1
  # GPT-SoVITS サービスのポート
  port: 9880
  # オーディオの一時フォルダ
  tmp_dir: .tmp/wav_output
```

ここで、

1. `debug`：Flask サービスをデバッグモードで起動するかどうかを示します。デフォルトは `False` です。
2. `host`：GPT-SoVITS サービスのホストアドレスです。ローカルマシンで起動している場合、デフォルトは `127.0.0.1` です。
3. `port`：GPT-SoVITS サービスのポート番号です。変更していない場合、デフォルトポートは `9880` です。
4. `tmp_dir`
   ：生成されたオーディオファイルを一時的に保存するディレクトリです。適切な場所を選択してください。デフォルトは `.tmp/wav_output`
   です。

#### 音声分析サービスの設定

仮想キャラクターが異なる音声で話すためには、`template/tone_list.yaml` の設定を変更してカスタムプロンプトを設定する必要があります。以下は例です。

```yaml
EMOTION_ID:
  refer_wav_path: 1.wav
  prompt_text: こんにちは、よろしくお願いします。
  prompt_language: ja
```

ここで、

1. `EMOTION_ID` はこのプロンプトが含む音声の表情を示します。例えば、「`幸せ`」、「`怒り`」などです。使用する大規模な言語モデルによっては、EMOTION_ID
   を設定すると効果が高まる可能性があります。
2. `refer_wav_path`：このプロンプトのオーディオファイルのパスです。**オーディオの長さは 3 秒以上でなければならず、10
   秒未満である必要があります**。
3. `prompt_text`：オーディオファイルで表現されている内容です。
4. `prompt_language`：このプロンプトで使用される言語です。GPT-SoVITS は現在`zh`（中国語）、`en`（英語）、`ja`
   （日本語）の3つの言語をサポートしています。

#### ChatGLM3 サービスの設定

[ChatGLM3](https://github.com/THUDM/ChatGLM3) はこのプロジェクトの中核であり、このサービスを正しく起動しないとプロジェクトを開始できません。以下は設定ファイルです：

```yaml
# ChatGLM3 サービスの設定
chatglm3_service_config:
  # デバッグモードで実行するかどうか
  debug: False
  # ChatGLM3 サービスのホスト
  host: 127.0.0.1
  # ChatGLM3 サービスのポート
  port: 8085
  # トークナイザのパス
  tokenizer_path: THUDM/chatglm3-6b
  # モデルのパス
  model_path: THUDM/chatglm3-6b
  # 量子化レベル
  quantize: 4
```

ここで、

1. `debug`：Flask がデバッグモードで起動するかどうかを指定するパラメータで、デフォルトは `False` です。
2. `host`：ChatGLM3 サービスのホストアドレスで、ローカルマシンで起動している場合はデフォルトで `127.0.0.1` です。
3. `port`：ChatGLM3 サービスのポート番号で、変更していない場合はデフォルトポートが `8085` です。
4. `tokenizer_path`：ChatGLM のモデルディレクトリへのパスです。
5. `model_path`：ChatGLM のトークナイザディレクトリであり、通常は `tokenizer_path` と同じです。
6. `quantize`：ChatGLM の量子化レベルで、通常は 4 ですが、GPU メモリが大きく、より大きな量子化レベルをサポートできる場合は 8
   を使用することができます。

#### OBS サービスの設定

[OBS](https://obsproject.com/download)
は無料かつオープンソースのビデオ録画および配信ソフトウェアです。以下の設定ファイルは、関連する字幕を表示できるようにするためのものです。もちろん、ライブ配信などの機能が不要な場合は、この設定ファイルを使用する必要はありません。

```yaml
# OBS サービスの設定
obs_config:
  # 弾幕出力ファイルのパス
  danmaku_output_path: .tmp/danmaku_output/output.txt
  # トーン出力ファイルのパス
  tone_output_path: .tmp/tone_output/output.txt
  # 大規模言語モデル出力ファイルのパス
  llm_output_path: .tmp/llm_output/output.txt
```

ここで、

1. `danmaku_output_path`：選択された弾幕がこのパスのファイルに出力されます。
2. `tone_output_path`：モデルが出力した音声のトーンがこのパスのファイルに出力されます。
3. `llm_output_path`：モデルが出力したテキストがこのパスのファイルに出力されます。

#### Zerolan の設定

以下は、プロジェクトの設定ファイルです。

```yaml
# プロジェクトの設定
zerolan_live_robot_config:
  # カスタムプロンプトテンプレート
  custom_prompt_path: template/custom_prompt.json
```

`custom_prompt.json` の中身は以下のようになります：

```json
{
  "query": "",
  "history": [
    {
      "content": "あなたは今、猫の女の子です。何を言っても「にゃん」と付ける必要があります。覚えたら、「了解、ご主人さまにゃん！」と返信するだけです。",
      "metadata": "",
      "role": "user"
    },
    {
      "content": "了解、ご主人さまにゃん！",
      "metadata": "",
      "role": "assistant"
    },
    {
      "content": "今、あなたは何ですか？",
      "metadata": "",
      "role": "user"
    },
    {
      "content": "ご主人さま、私は猫の女の子にゃん！",
      "metadata": "",
      "role": "assistant"
    }
  ],
  "temperature": 1,
  "top_p": 1
}
```

ここでは、`history`
リストにいくつかの対話ラウンドを追加することができます。必要に応じて編集および拡張してください。ここでの `role`
プロパティでは、`user` はユーザーの入力を表し、`assistant` はモデルの出力を表します。

## 実行を開始する

まず、ChatGLM3 サービスを起動します。

```shell
cd YourDirectory/ZerolanLiveRobot # リポジトリのディレクトリに移動
conda activate zerolanliverobot # 作成した仮想環境をアクティブ化
python api_run.py # ChatGLM3 を起動
```

大規模言語モデルの読み込みには時間がかかる場合がありますので、しばらくお待ちください。

次に、GPT-SoVTIS サービスを起動します。起動スクリプトは、元の GPT-SoVTIS プロジェクトのドキュメントに従って設定してください。

ChatGLM3 と GPT-SoVTIS が正しく起動していることを確認したら、以下のコードを実行してプロジェクトを起動できます。

```shell
cd YourDirectory/ZerolanLiveRobot # リポジトリのディレクトリに移動
conda activate zerolanliverobot # 作成した仮想環境をアクティブ化
python main.py # メインプログラムを起動
```

すべてが正常に動作していれば、まもなく合成された音声が自動的に再生されるはずです（システムの音量にご注意ください）。

Minecraft AI Agent を使用してサーバーで遊ぶ場合は、以下のコマンドを使用できます。

```shell
node minecraft/service.js host port username password
```

ここで、

1. `host`：Minecraft サーバーのアドレス。ローカルでサーバーを実行している場合は `127.0.0.1` を使用してください。
2. `port`：Minecraft サーバーのポート。デフォルトのポートを変更していない場合は通常 `25565` です。
3. `username`：Minecraft AI Agent がサインインするサーバーのプレイヤー名。ゲーム内で表示される名前です。
4. `password`：Minecraft AI Agent がサインインするサーバーのパスワード。パスワードを設定していない場合はこのフィールドは無視してください。

## FAQ

#### GPT-SoVTIS サービスに接続できない

```
CRITICAL | gptsovits.service:init:26 - ❌️ GPT-SoVTIS 服务无法连接至 http://127.0.0.1:9880
```

このようなエラーが発生する場合、プログラムが `http://127.0.0.1:9880`（設定によっては異なる場合があります）にアクセスできません。GPT-SoVITS
プロジェクトで api サービスが正しく起動しているかを確認してください。`api.py` または `api2.py` を実行しており、`webui.py`
を実行していないことを確認してください。

#### ウィンドウが見つからない

```
WARNING  | scrnshot.service:screen_cap:32 - 无法找到窗口 xxx
```

文字通りの意味ですが、プログラムが設定ファイルで指定された `screenshot_config.win_title`
で指定されたウィンドウを見つけられません。指定したウィンドウが開いているか、またはスペルミスがないかを確認してください。

## オープンソースライセンス

このプロジェクトは「GNU GENERAL PUBLIC LICENSE (GPLv3)」を使用しており、ユーザーが自由にプロジェクトから利益を得られるようにしています。

## 特別な感謝

このプロジェクトで以下のオープンソースプロジェクトの一部またはすべての技術を使用しており、オープンソースコミュニティに人類社会への貢献に感謝します。

[THUDM/ChatGLM3: ChatGLM3 series: Open Bilingual Chat LLMs | 开源双语对话语言模型 (github.com)](https://github.com/THUDM/ChatGLM3)

[RVC-Boss/GPT-SoVITS: 1 min voice data can also be used to train a good TTS model! (few shot voice cloning) (github.com)](https://github.com/RVC-Boss/GPT-SoVITS)

[Salesforce/blip-image-captioning-large · Hugging Face](https://huggingface.co/Salesforce/blip-image-captioning-large)

[Nemo2011/bilibili-api: 哔哩哔哩常用API调用。支持视频、番剧、用户、频道、音频等功能。原仓库地址：https://github.com/MoyuScript/bilibili-api](https://github.com/Nemo2011/bilibili-api)

[PrismarineJS/mineflayer: Create Minecraft bots with a powerful, stable, and high level JavaScript API. (github.com)](https://github.com/PrismarineJS/mineflayer)

ここに記載されていないものも含まれているかもしれません。不足があれば、開発者に連絡してください。

## 連絡先

プロジェクトに関するご意見やご質問などがある場合は、以下の連絡先で開発者にお問い合わせください。

Email：AkagawaTsurunaki@outlook.com

QQ Group：858378209

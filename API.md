# 暂时可用的API

## Blip

默认服务地址：`http://127.0.0.1:5926`

### 推理

POST: `/blip/infer`

#### 请求体
```json
{
  "img_path": "examples/img/neko.png",
  "prompt": "There"
}
```
#### 响应体


当推理成功时
```json
{
  "ok": true,
  "msg": "Blip 推理成功",
  "data": {
    "caption": "There is a cat sitting on the blue table."
  }
}
```

当图片路径不存在时
```json
{
  "ok": false,
  "msg": "图片路径不存在",
  "data": null
}
```

## Chat GLM 3 Service
默认服务地址：`http://127.0.0.1:8085`

### 非流式推理
GET：`chatglm3/predict`

### 流式推理
GET：`chatglm3/streampredict`

#### 请求体

```json
{
  "query": "",
  "history": [
    {
      "content": "",
      "metadata": "",
      "role": "user"
    },
    {
      "content": "",
      "metadata": "",
      "role": "assistant"
    }
  ],
  "temperature": 1,
  "top_p": 1
}
```
#### 响应体


## ASR

```json
{
  "wav_path": "examples/asr/hello.wav"
}
```
当推理成功时
```json
{
  "ok": true,
  "msg": "推理成功",
  "data": {
    "transcript": "这是一段测试"
  }
}
```
当音频路径不存在时
```json
{
  "ok": false,
  "msg": "无法找到音频路径",
  "data": null
}
```
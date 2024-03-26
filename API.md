# 暂时可用的API

## Blip

默认服务地址：`http://127.0.0.1:5926`

POST: `/blip/infer`

### 请求体
```json
{
  "img_path": "examples/img/neko.png",
  "prompt": "There"
}
```
### 响应体

#### 当推理成功时
```json
{
  "ok": true,
  "msg": "Blip 推理成功",
  "data": {
    "caption": "There is a cat sitting on the blue table."
  }
}
```

#### 当图片路径不存在时
```json
{
  "ok": false,
  "msg": "图片路径不存在",
  "data": null
}
```
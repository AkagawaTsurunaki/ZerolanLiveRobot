# ZerolanLive2D

>  [正在开发……]

## 主要实现

| 实现                 | 描述                                                         |
| -------------------- | ------------------------------------------------------------ |
| ZerolanLive2D 控制器 | 基于 Unity 开发的可以通过 API 调用加载并控制 Live2D 模型的控制器。 |
| ZerolanLive2D 协议   | 设计并实现了基于 WebSocket 的自定义 ZerolanLive2D 协议，用以与主项目 ZerolanLiveRobot 的附属线程交换 JSON 数据，从而实现对 Live2D 模型进行初始化、加载、控制等功能。 |

> [!NOTE]
>
> 在 Unity 2021.3.44f1c1 中使用的依赖项：Newtonsoft Json、UnityWebSocket、Live2D SDK

## API

任何请求都遵循以下格式。

```json
{
    "Protocol": "Zerolan Live2D Protocol",
    "Version": "0.1",
    "Event": "client_hello",
    "Data": ...
}
```

此后我们将不再展示 `Protocol` 和 `Version` 字段，但是它们应该存在于协议中。

以下我们称 Zerolan Live Robot 为**服务端**（WebSocket），Zerolan Live2D 为**客户端**（WebSocket）。

### Client Hello

由客户端发起，用于通知服务端，本客户端已经初始化完毕。

```json
{
    "Event": "client_hello",
    "Data": null
}
```

### Server Hello

由服务端发起，用于通知客户端，服务端已经正确识别客户端。

```json
{
    "Event": "server_hello",
    "Data": null
}
```

### Load Live2D Model

由服务端发起，用于告知客户端加载模型。

```json
{
    "Event": "load_live2d_model",
    "Data": {
        "ModelDirectory": "live2d/model_name" // Live2D 模型文件夹所在路径
    }
}
```

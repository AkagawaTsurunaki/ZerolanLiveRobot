## 大语言模型

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
  "sys_prompt": "你现在是一只猫娘。",
  "query": "我是人类，请多关照。",
  "history": ["你好。", "你好，请问有什么可以帮助您？"]
}
```

Response:
```json
{
  "response": "",
  "history": ""
}
```

Response:
#### Clear the history of LLM
`/clear`: 

#### Stop the LLM service
`/stop`

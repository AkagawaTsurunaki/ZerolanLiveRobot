@echo off

rem 设置编码为 UTF-8
chcp 65001

:restart

rem 激活 conda 环境
call activate zerolanliverobot

rem 这里修改 GPT_SOVITS 的路径，运行地址和端口号，为了效率自动使用流式编程
cd %ZEROLAN_LIVE_ROBOT%
python service_starter.py --service asr
set return_code=%ERRORLEVEL%
echo 错误码 %return_code%
echo LLM 服务意外终止，正在尝试重新启动……
timeout /t 1 /nobreak >nul
goto restart

:terminate
pause
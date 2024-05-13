@echo off

rem 设置编码为 UTF-8
chcp 65001

:restart

rem 激活 conda 环境
call activate gptsovits

rem 这里修改 GPT_SOVITS 的路径，运行地址和端口号，为了效率自动使用流式编程
cd %GPT_SOVITS_PATH%
python api.py -d cuda -a 127.0.0.1 -p 9880 -sm n
set return_code=%ERRORLEVEL%
echo Error code %return_code%
echo GPT-SoVITs 模型服务意外终止，正在尝试重新启动……
timeout /t 1 /nobreak >nul
goto restart

:terminate
pause
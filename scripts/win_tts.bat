@echo off
call activate GPTSoVits

cd ../../

rem 注意修改您自己的 GPT-SoVITS 路径
set project_dir="../GPT-SoVITS"

cd /d %project_dir% || (
    echo Cannot find the project folder %project_dir%.
    echo To solve this problem, you may try:
    echo 1. Check if the directory exists.
    echo 2. Download GPT-SoVITS from https://github.com/AkagawaTsurunaki/GPT-SoVITS
    pause
    exit /b 1
)

python api.py -p 11006

@echo off
call activate GPTSoVits

cd %GPT_SOVITS_PROJECT_DIR%

python api.py -p 11006

pause

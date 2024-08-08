@echo off
call activate chatglm3

cd %ZEROLAN_LIVE_ROBOT_PROJECT_DIR%
python service_starter.py --service llm
pause
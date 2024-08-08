@echo off
call activate paraformer

cd %ZEROLAN_LIVE_ROBOT_PROJECT_DIR%
python service_starter.py --service asr
pause

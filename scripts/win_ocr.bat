@echo off
call activate paddle

cd %ZEROLAN_LIVE_ROBOT_PROJECT_DIR%
python service_starter.py --service ocr
pause
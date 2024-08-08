@echo off
call activate blip

cd %ZEROLAN_LIVE_ROBOT_PROJECT_DIR%
python service_starter.py --service img_cap
pause
@echo off
cd /d D:\REDKINA\project
python app.py %*
start chrome "http://127.0.0.1:5000"
pause
@echo off
pyinstaller -Fw main.py --add-data="donate.png;."
pause

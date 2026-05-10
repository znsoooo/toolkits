@echo off
for /f "delims=" %%i in ('dir /ad /b /s ^| sort /r') do (rd "%%i" 2>nul)
pause

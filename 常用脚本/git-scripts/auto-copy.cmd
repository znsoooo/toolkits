@echo off
for /f "delims=" %%i in ('where git') do (
    copy /y *.bat "%%~dpi"
    goto :exit
)
:exit
pause

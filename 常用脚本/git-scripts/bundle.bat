@echo off
for %%i in ("%cd%") do for /f %%j in ('git rev-parse --abbrev-ref HEAD') do git bundle create "%%~ni.%%j%1.git" %%j %1
pause

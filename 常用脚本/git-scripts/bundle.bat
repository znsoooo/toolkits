@echo off
for %%i in ("%cd%") do git bundle create "%%~nxi%1.git" --all %1
:: for %%i in ("%cd%") do git bundle create "%%~nxi.HEAD%1.git" HEAD %1
:: for %%i in ("%cd%") do for /f %%j in ('git rev-parse --abbrev-ref HEAD') do git bundle create "%%~nxi.%%j%1.git" %%j %1
pause

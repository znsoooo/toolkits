@echo off
(for %%i in ("%~1\*.mp4") do (echo file '%%i')) > %1.txt
ffmpeg -y -f concat -safe 0 -i %1.txt -c:v copy -c:a aac %1.mp4
del %1.txt
pause

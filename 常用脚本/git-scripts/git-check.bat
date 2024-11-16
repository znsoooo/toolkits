@echo off
chcp 65001 > nul

set red=[33m
set end=[0m

echo atime/ctime not same:
for /f "tokens=1,2,3,*" %%b in ('git log --format^="%%h %%aI %%cI %%s"') do if not %%c == %%d echo   %red%git log -1 %%b%end% %%e
echo.

setlocal enabledelayedexpansion
echo time not increasing:
set time2=9999999999
for /f "tokens=1,2,*" %%i in ('git log --format^="%%h %%at %%s"') do (
    if !time2! leq %%j echo   %red%git log %%i..!hash2!%end% !subject2!
    set hash2=%%i
    set time2=%%j
    set subject2=%%k
)
echo.

call cmd

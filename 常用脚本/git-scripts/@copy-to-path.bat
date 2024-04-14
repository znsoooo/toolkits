@echo off

for /f "delims=" %%i in ('where git') do (
    set "folder=%%~dpi"
    goto :done
)
:done

echo Copy to folder:
echo   "%folder%"
echo.

copy /y bundle.bat "%folder%"
copy /y git-edit.bat "%folder%"
copy /y git-check.bat "%folder%"
copy /y git-rewrite.bat "%folder%"
echo.

pause

@echo off

set base=http://127.0.0.1/repos

:: Read the folder name and concatenate URL
for %%i in ("%cd%") do set name=%%~ni
set url=%base%/%name%.git

:: Push all local remote branches to the remote local branches
git push --tags %url% refs/remotes/origin/*:refs/heads/*
echo.

pause

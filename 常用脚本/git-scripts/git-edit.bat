@echo off
chcp 65001 > nul

git log --reverse --format="%%h %%aI %%s" > git-log.txt
git-log.txt
pause

git stash -q
set first=
for /f "tokens=1,2,*" %%i in (git-log.txt) do (
    if not defined first (
        set first=1
        git reset --hard %%i
    ) else (
        git cherry-pick %%i
    )
    set GIT_COMMITTER_DATE=%%j
    git commit --amend --no-edit --quiet --date=%%j
    echo ----------
)
git stash pop -q
pause

:: overwrite author:
:: git commit --amend --no-edit --quiet --author "Shixian Li <lsx7@sina.com>"

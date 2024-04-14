@echo off

git log --reverse --format="%%H %%aI %%s" > git-log.txt
git-log.txt
pause

git stash -q
set first=
for /f "tokens=1,2" %%i in (git-log.txt) do (
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

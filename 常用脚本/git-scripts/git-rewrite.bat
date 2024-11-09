@echo off
git stash -q
echo ----------
set first=
for /f "tokens=1,2,3" %%i in ('git log --reverse --format^="%%h %%at %%ct"') do (
    set GIT_COMMITTER_DATE=%%j
    if defined first (
        echo ----------
        git cherry-pick %%i
    ) else if not %%j == %%k (
        set first=1
        git reset --hard %%i
        git commit --amend --no-edit --quiet
    )
)
echo ----------
git stash pop -q
pause

:: overwrite author:
:: git commit --amend --no-edit --quiet --author "Shixian Li <lsx7@sina.com>"

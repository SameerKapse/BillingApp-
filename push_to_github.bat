
@echo off
setlocal
title Push BillingApp to GitHub

echo ========================================
echo       BillingApp - GitHub Push
echo ========================================
echo.

:: Configure Git identity
git config --global user.name "Sameer Kapse"
git config --global user.email "sameerkapse43@gmail.com"

:: Initialize Git if needed
if not exist ".git" (
    git init
    if errorlevel 1 goto error
)

:: Exclude sensitive and unnecessary files
if not exist ".gitignore" (
    (
        echo .env
        echo .env.*
        echo !.env.example
        echo node_modules/
        echo venv/
        echo __pycache__/
        echo *.log
        echo *.pem
        echo *.key
        echo secrets.json
    ) > .gitignore
)

:: Stage project files
git add .
if errorlevel 1 goto error

:: Commit changes
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "Update BillingApp project"
    if errorlevel 1 goto error
) else (
    echo No new changes to commit.
)

:: Set main branch
git branch -M main
if errorlevel 1 goto error

:: Configure repository
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    git remote add origin https://github.com/SameerKapse/BillingApp-.git
) else (
    git remote set-url origin https://github.com/SameerKapse/BillingApp-.git
)
if errorlevel 1 goto error

:: Push to GitHub
echo.
echo Pushing project to GitHub...
git push -u origin main
if errorlevel 1 goto error

echo.
echo SUCCESS: Project pushed to GitHub!
echo https://github.com/SameerKapse/BillingApp-
pause
exit /b 0

:error
echo.
echo ERROR: Operation failed. Check the Git error above.
pause
exit /b 1
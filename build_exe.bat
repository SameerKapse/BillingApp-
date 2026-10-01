@echo off
title Building Billing Application (.exe)
echo ==================================================
echo   Building Standalone Billing Application (.exe)
echo ==================================================

python build_exe.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Build failed! Check the errors above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==================================================
echo   Build Successful! Executable is in: dist\BillingApp.exe
echo ==================================================
pause

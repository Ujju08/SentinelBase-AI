@echo off
title DefenceSite AI Platform
echo ========================================================
echo   DEFENCESITE AI - 3D SPATIAL PLATFORM
echo ========================================================
echo.
cd /d "%~dp0"

python app.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo --------------------------------------------------------
    echo If Python is not recognized, trying 'py app.py'...
    echo --------------------------------------------------------
    py app.py
)

echo.
echo ========================================================
echo If an error occurred above, please check the message.
echo ========================================================
pause

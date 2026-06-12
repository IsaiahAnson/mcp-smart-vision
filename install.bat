@echo off
setlocal enabledelayedexpansion

echo ========================================
echo MCP Remote Desktop Control Server v2.4
echo Smart Path & Installation Mode
echo ========================================

:: Switch to the directory where the batch file is located
cd /d "%~dp0"
echo Working directory set to: %cd%

echo.
echo Running initial diagnostics...
python debug_logger.py

echo.
echo Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Running post-install check...
python debug_logger.py

echo ========================================
echo Installation Complete!
echo Check 'debug_install.log' for details.
echo ========================================
pause

@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo 虚拟环境不存在，请先创建虚拟环境
    pause
    exit /b 1
)

python main.py
pause
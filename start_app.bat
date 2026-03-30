@echo off
chcp 65001 >nul
echo ========================================
echo   Everify 网页核查自动化系统
echo   正在启动 Web 服务...
echo ========================================
echo.

REM 激活虚拟环境
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo 警告: 未找到虚拟环境，尝试使用系统 Python
)

REM 启动 Flask 应用
echo 启动地址: http://localhost:5000
echo.
python web\app.py

echo.
echo 应用程序已退出
pause

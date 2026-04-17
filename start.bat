@echo off
chcp 65001 >nul
echo ============================================
echo   Flow Image CLI - 启动脚本
echo ============================================

:: 检查虚拟环境
if not exist .venv (
    echo [错误] 未找到虚拟环境 .venv
    echo   请先运行 setup.bat 安装
    pause
    exit /b 1
)

:: API Key 配置（可自行修改）
set FLOW_API_KEY=flow-server-key
set PYTHONPATH=%CD%

echo.
echo   API Key: %FLOW_API_KEY%
echo   服务地址: http://0.0.0.0:8787
echo   首次使用需访问 http://localhost:8787/setup 授权
echo.
echo ============================================
echo.

call .venv\Scripts\activate.bat

.venv\Scripts\python.exe -m uvicorn flow_cli.api_server:app --host 0.0.0.0 --port 8787

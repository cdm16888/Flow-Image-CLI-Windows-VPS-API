@echo off
chcp 65001 >nul
echo ============================================
echo   Flow Image CLI - 一键安装脚本
echo ============================================
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.12+
    echo   下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] 检查 Python 版本...
for /f "delims=" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo      %PYTHON_VERSION%

echo.
echo [2/5] 创建虚拟环境...
if exist .venv (
    echo      .venv 已存在，跳过
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo      完成
)

echo.
echo [3/5] 激活虚拟环境并安装依赖...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [错误] 激活虚拟环境失败
    pause
    exit /b 1
)
echo      已激活虚拟环境

echo.
echo [4/5] 安装 Python 依赖包（约 50MB）...
.venv\Scripts\pip.exe install --upgrade pip
.venv\Scripts\pip.exe install fastapi uvicorn[standard] aiohttp pyyaml playwright Pillow python-multipart tomli curl-cffi
if %errorlevel% neq 0 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)
echo      完成

echo.
echo [5/5] 安装 Playwright Chromium 浏览器（约 170MB）...
.venv\Scripts\python.exe -m playwright install chromium
if %errorlevel% neq 0 (
    echo [错误] Playwright 安装失败
    pause
    exit /b 1
)
echo      完成

echo.
echo ============================================
echo   安装完成！
echo ============================================
echo.
echo   下一步：双击运行 start.bat 启动服务
echo.
echo   首次启动后需访问 http://windowsvpshost:8787/setup
echo   完成 Google 账号授权
echo.
echo   默认 API Key: flow-server-key
echo   服务地址: http://0.0.0.0:8787
echo.
pause

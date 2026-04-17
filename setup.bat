@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo   Flow Image CLI Windows VPS - 一键安装脚本
echo ============================================
echo.

:: 查找 Python 解释器
set PYTHON_EXE=
where python >nul 2>&1
if %errorlevel% equ 0 set PYTHON_EXE=python
if not defined PYTHON_EXE (
    where py >nul 2>&1
    if %errorlevel% equ 0 set PYTHON_EXE=py
)

:: 检查 uv（推荐，可绕过 PATH 问题）
if not defined PYTHON_EXE (
    where uv >nul 2>&1
    if %errorlevel% equ 0 (
        echo [提示] 使用 uv 找到 Python
        set PYTHON_EXE=uv run python
    )
)

if not defined PYTHON_EXE (
    echo [错误] 未找到 Python，请先安装 Python 3.12+
    echo   下载地址: https://www.python.org/downloads/
    echo   安装时请勾选 "Add Python to PATH"
    echo   或安装 uv: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

echo [找到 Python: %PYTHON_EXE%]
echo.

:: 检查 Python 版本
for /f "delims=" %%v in ('%PYTHON_EXE% --version 2^>^&1') do set PYTHON_VERSION=%%v
echo [Python 版本: !PYTHON_VERSION!]
echo.

:: 创建虚拟环境
echo [1/5] 创建虚拟环境 .venv ...
if exist .venv (
    echo      .venv 已存在，跳过
) else (
    %PYTHON_EXE% -m venv .venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo      完成
)

echo.
echo [2/5] 激活虚拟环境并安装依赖...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 激活虚拟环境失败
    pause
    exit /b 1
)
echo      已激活

echo.
echo [3/5] 安装 Python 依赖包（约 50MB）...
.venv\Scripts\pip.exe install --upgrade pip
.venv\Scripts\pip.exe install fastapi "uvicorn[standard]" aiohttp pyyaml playwright Pillow python-multipart tomli curl-cffi
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)
echo      完成

echo.
echo [4/5] 安装 Playwright Chromium 浏览器（约 170MB）...
.venv\Scripts\python.exe -m playwright install chromium
if errorlevel 1 (
    echo [错误] Playwright 安装失败
    pause
    exit /b 1
)
echo      完成

echo.
echo [5/5] 验证安装...
.venv\Scripts\python.exe -c "import fastapi,uvicorn,playwright; print('依赖验证 OK')"
if errorlevel 1 (
    echo [错误] 依赖验证失败
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
echo   首次启动后需访问 http://localhost:8787/setup
echo   完成 Google 账号授权（Token 有效期约 24 小时）
echo.
echo   默认 API Key: flow-server-key
echo   服务地址: http://0.0.0.0:8787
echo.
pause

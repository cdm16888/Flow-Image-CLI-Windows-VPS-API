# Flow Image CLI Windows VPS - 一键安装脚本
# 使用方法: 右键 -> 用 PowerShell 运行

$ErrorActionPreference = "Stop"
$BASE_DIR = $PSScriptRoot

Write-Host "============================================"
Write-Host "  Flow Image CLI Windows VPS - 安装脚本"
Write-Host "============================================"
Write-Host ""

# 1. 检查 uv
Write-Host "[1/5] 检查 uv..."
$uvCmd = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uvCmd) {
    Write-Host "[错误] 未找到 uv，请先安装 uv: https://github.com/astral-sh/uv"
    Write-Host "   Windows 安装: pip install uv"
    Read-Host "按回车退出"
    exit 1
}
$uvVersion = (uv --version).Split()[0]
Write-Host "      uv $uvVersion  OK"
Write-Host ""

# 2. 创建虚拟环境
Write-Host "[2/5] 创建虚拟环境 .venv ..."
if (Test-Path "$BASE_DIR\.venv") {
    Write-Host "      .venv 已存在，跳过"
} else {
    uv venv "$BASE_DIR\.venv"
    if ($LASTEXITCODE -ne 0) { throw "创建虚拟环境失败" }
    Write-Host "      完成"
}
Write-Host ""

# 3. 安装依赖
Write-Host "[3/5] 安装 Python 依赖包 (~50MB)..."
uv pip install --python "$BASE_DIR\.venv\Scripts\python.exe" fastapi "uvicorn[standard]" aiohttp pyyaml playwright Pillow python-multipart tomli curl-cffi
if ($LASTEXITCODE -ne 0) { throw "安装依赖失败" }
Write-Host "      完成"
Write-Host ""

# 4. 安装 Playwright Chromium
Write-Host "[4/5] 安装 Playwright Chromium (~170MB)..."
& "$BASE_DIR\.venv\Scripts\python.exe" -m playwright install chromium
if ($LASTEXITCODE -ne 0) { throw "Playwright 安装失败" }
Write-Host "      完成"
Write-Host ""

# 5. 验证
Write-Host "[5/5] 验证安装..."
& "$BASE_DIR\.venv\Scripts\python.exe" -c "import fastapi,uvicorn,playwright; print('依赖验证 OK')"
if ($LASTEXITCODE -ne 0) { throw "依赖验证失败" }
Write-Host "      完成"
Write-Host ""

Write-Host "============================================"
Write-Host "  安装完成!"
Write-Host "============================================"
Write-Host ""
Write-Host "  下一步: 右键 start.ps1 -> 用 PowerShell 运行"
Write-Host ""
Write-Host "  首次启动后访问 http://localhost:8787/setup"
Write-Host "  完成 Google 账号授权 (Token 有效期约 24 小时)"
Write-Host ""
Write-Host "  默认 API Key: flow-server-key"
Write-Host "  服务地址: http://0.0.0.0:8787"
Write-Host ""
Read-Host "按回车退出"

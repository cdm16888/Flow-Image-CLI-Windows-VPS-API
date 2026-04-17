# Flow Image CLI Windows VPS - 启动脚本
# 使用方法: 右键 -> 用 PowerShell 运行

$ErrorActionPreference = "Stop"
$BASE_DIR = $PSScriptRoot

Write-Host "============================================"
Write-Host "  Flow Image CLI Windows VPS - 启动脚本"
Write-Host "============================================"
Write-Host ""

# 检查虚拟环境
if (-not (Test-Path "$BASE_DIR\.venv")) {
    Write-Host "[错误] 未找到虚拟环境 .venv"
    Write-Host "  请先运行 setup.ps1 安装"
    Read-Host "按回车退出"
    exit 1
}

$env:FLOW_API_KEY = "flow-server-key"
$env:PYTHONPATH = $BASE_DIR

Write-Host "  API Key: $env:FLOW_API_KEY"
Write-Host "  服务地址: http://0.0.0.0:8787"
Write-Host "  首次使用需访问 http://localhost:8787/setup 授权"
Write-Host ""
Write-Host "============================================"
Write-Host ""

# 启动服务
& "$BASE_DIR\.venv\Scripts\python.exe" -m uvicorn flow_cli.api_server:app --host 0.0.0.0 --port 8787

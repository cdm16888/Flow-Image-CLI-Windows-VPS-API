# Flow Image CLI Windows VPS API

> 在 Windows VPS 上本地运行 Google Flow 图片生成 API，支持 OpenAI 格式调用

## 功能

- 将 Google Flow 图片生成能力封装为本地 API 服务
- 兼容 OpenAI ChatCompletions 接口格式
- 支持 nano-banana-2 / nano-banana-pro 等模型
- 支持 4K / 1080p / 720p / 480p 多种分辨率
- 支持横屏 / 竖屏 / 方形 / 超宽多种比例

## 系统要求

- Windows Server / Windows 10+（VPS 或本地电脑）
- Python 3.12+
- 网络要求：**干净的住宅 IP**（Residential IP）
  - 若使用数据中心 IP（DC IP）或被 Google 标记的 IP，Playwright 浏览器会被验证拦截
  - 如遇验证页面卡住，请开启系统 TUN 模式（Clash Verge 等代理软件的 TUN 模式）让浏览器流量走代理

## 一键安装

下载本项目后，双击运行：

```
setup.bat
```

或以管理员身份运行 PowerShell：

```powershell
.\setup.bat
```

安装过程会自动：
1. 创建 Python 虚拟环境（`.venv`）
2. 安装所有依赖包（fastapi、uvicorn、playwright 等）
3. 安装 Playwright Chromium 浏览器（约 170MB）

## 一键启动

```
start.bat
```

启动后显示：
```
Flow API Server
API Key: your-secret-key
Started on http://0.0.0.0:8787
```

服务默认绑定 `0.0.0.0:8787`，局域网/公网均可访问。

## 首次登录授权

启动服务后，首次调用 API 前需要完成 Google 账号授权：

1. 在 VPS/本地打开浏览器访问：`http://windowsvpshost:8787/setup`
2. 点击「**重新登录**」，在弹出窗口登录 Google 账号
3. 登录成功后点击「**重新同步**」
4. 之后 API 即可正常调用

> 授权有效期约 24 小时，过期后重新访问 `http://windowsvpshost:8787/setup` 重新登录即可。

## API 调用示例

### CURL

```bash
curl -X POST http://windowsvpshost:8787/v1/chat/completions \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"nano-banana-2-landscape\",\"messages\":[{\"role\":\"user\",\"content\":\"a fluffy orange cat\"}]}"
```

### Python

```python
import requests

resp = requests.post(
    "http://windowsvpshost:8787/v1/chat/completions",
    headers={"Authorization": "Bearer your-secret-key"},
    json={
        "model": "nano-banana-2-landscape",
        "messages": [{"role": "user", "content": "a fluffy orange cat"}]
    },
    timeout=120
)
print(resp.json()["choices"][0]["message"]["content"])
```

### OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-secret-key",
    base_url="http://windowsvpshost:8787/v1"
)
# 注意：model 名称需使用 nano-banana-2 / nano-banana-pro，不支持 gpt-4o 等
```

## API 地址配置

| 项目 | 默认值 |
|------|--------|
| 服务地址 | `http://0.0.0.0:8787` |
| API Key | `flow-server-key`（可在 `start.bat` 中修改） |
| 健康检查 | `http://windowsvpshost:8787/health` |
| 授权页面 | `http://windowsvpshost:8787/setup` |

### 修改 API Key

编辑 `start.bat`，找到：
```bat
set FLOW_API_KEY=flow-server-key
```
改为你的密钥即可。

## 支持的模型

| 模型 | 说明 |
|------|------|
| `nano-banana-2-landscape` | 横屏（16:9）|
| `nano-banana-2-portrait` | 竖屏（9:16）|
| `nano-banana-2-square` | 方形（1:1）|
| `nano-banana-2-ultrawide` | 超宽（21:9）|
| `nano-banana-pro-landscape` | 横屏 Pro |
| `nano-banana-pro-portrait` | 竖屏 Pro |
| `nano-banana-pro-square` | 方形 Pro |

## 常见问题

### Q: API 返回 401 Unauthorized
检查 `start.bat` 中的 `FLOW_API_KEY` 是否与调用端一致，默认密钥为 `flow-server-key`。

### Q: API 返回 500 Internal Server Error
1. 确认已通过 `http://windowsvpshost:8787/setup` 完成 Google 账号授权
2. Token 可能已过期，重新访问授权页面登录

### Q: 调用成功但图片下载失败
图片保存在 `C:\Users\<用户名>\AppData\Windows VPS\Temp\2\flow-image-api\`，确保磁盘空间充足。

### Q: 浏览器验证（reCAPTCHA）卡住不动
这是因为 Google 检测到当前 IP 为数据中心/非住宅 IP。解决方案：
1. **使用干净的住宅 IP**（推荐）
2. 或开启代理软件的 **TUN 模式**（全局代理），让 Playwright 浏览器流量走代理

### Q: 端口 8787 被占用
编辑 `start.bat`，把 `8787` 改成其他端口（如 `8080`），同时更新 API 调用地址。

## 网络要求说明

Google Flow 对访问 IP 有严格检测，建议：

- 使用**住宅 IP（Residential IP）**的 VPS 或本地网络
- 数据中心 IP、被标记的 IP 可能无法完成 reCAPTCHA 验证
- 若无法更换 IP，建议开启 Clash Verge 等代理工具的 **TUN 模式**，将浏览器流量通过代理节点

## 目录结构

```
flow-image-cli-windowsvps-api/
├── setup.bat              # 一键安装脚本
├── start.bat              # 一键启动脚本
├── flow_cli/
│   ├── api_server.py      # API 服务主文件
│   ├── client.py          # Flow 客户端
│   ├── personal_captcha.py # Playwright 验证模块
│   ├── config.py          # 配置
│   └── models.py          # 数据模型
└── README.md
```

## 免责声明

本项目仅供学习交流使用，请遵守 Google Flow 的服务条款。使用本工具产生的任何问题由使用者自行承担。

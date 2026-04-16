"""
配置管理模块
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import tomli


@dataclass
class FlowConfig:
    """Flow 配置"""

    labs_base_url: str = "https://labs.google/fx/api"
    api_base_url: str = "https://aisandbox-pa.googleapis.com/v1"
    timeout: int = 120
    max_retries: int = 3


@dataclass
class CaptchaConfig:
    """验证码配置"""

    method: str = "personal"
    personal_headless: bool = False
    personal_timeout: int = 90
    personal_settle_seconds: float = 2.0


@dataclass
class TokenConfig:
    """Token 配置"""

    st: str = ""
    at: str = ""
    at_expires: str = ""
    project_id: str = ""
    user_paygate_tier: str = "PAYGATE_TIER_NOT_PAID"


@dataclass
class AppConfig:
    """应用配置"""

    flow: FlowConfig = field(default_factory=FlowConfig)
    captcha: CaptchaConfig = field(default_factory=CaptchaConfig)
    token: TokenConfig = field(default_factory=TokenConfig)
    output_dir: str = "output"
    debug: bool = False

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "AppConfig":
        """加载配置"""
        config = cls()

        if config_path is None:
            config_path = os.environ.get("FLOW_CONFIG", str(Path.home() / ".flow-cli" / "config.toml"))

        config_file = Path(config_path)
        if config_file.exists():
            try:
                with open(config_file, "rb") as f:
                    data = tomli.load(f)

                if "flow" in data:
                    for key, value in data["flow"].items():
                        if hasattr(config.flow, key):
                            setattr(config.flow, key, value)

                if "captcha" in data:
                    for key, value in data["captcha"].items():
                        if hasattr(config.captcha, key):
                            setattr(config.captcha, key, value)

                if "output" in data and isinstance(data["output"], dict):
                    if "output_dir" in data["output"]:
                        config.output_dir = data["output"]["output_dir"]
                elif "output_dir" in data:
                    config.output_dir = data["output_dir"]

                if "debug" in data and isinstance(data["debug"], dict):
                    if "enabled" in data["debug"]:
                        config.debug = bool(data["debug"]["enabled"])
                elif "debug" in data:
                    config.debug = bool(data["debug"])
            except Exception as e:
                print(f"加载配置文件失败: {e}")

        token_file = config_file.parent / "token.json"
        if token_file.exists():
            try:
                with open(token_file, "r", encoding="utf-8") as f:
                    token_data = json.load(f)
                for key, value in token_data.items():
                    if hasattr(config.token, key):
                        setattr(config.token, key, value)
            except Exception:
                pass

        return config

    def save_token(self, config_path: Optional[str] = None):
        """保存 Token 配置"""
        if config_path is None:
            config_path = str(Path.home() / ".flow-cli" / "config.toml")

        token_file = Path(config_path).parent / "token.json"
        token_file.parent.mkdir(parents=True, exist_ok=True)

        with open(token_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "st": self.token.st,
                    "at": self.token.at,
                    "at_expires": self.token.at_expires,
                    "project_id": self.token.project_id,
                    "user_paygate_tier": self.token.user_paygate_tier,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )


CONFIG: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """获取全局配置"""
    global CONFIG
    if CONFIG is None:
        CONFIG = AppConfig.load()
    return CONFIG


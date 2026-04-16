"""
Flow API 客户端
"""
import asyncio
import base64
import json
import random
import time
import uuid
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

try:
    from curl_cffi.requests import AsyncSession
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False
    import aiohttp

from .config import get_config
from .models import DEFAULT_MODEL, get_model_config
from .personal_captcha import get_personal_recaptcha_token


class FlowClient:
    """Flow API 客户端"""
    
    def __init__(self):
        self.config = get_config()
        self._user_agent_cache = {}
        
        self._default_headers = {
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "x-browser-channel": "stable",
            "x-browser-copyright": "Copyright 2026 Google LLC. All Rights reserved.",
            "x-browser-validation": "UujAs0GAwdnCJ9nvrswZ+O+oco0=",
            "x-browser-year": "2026",
            "x-client-data": "CJS2yQEIpLbJAQipncoBCNj9ygEIlKHLAQiFoM0BGP6lzwE="
        }
    
    def _generate_user_agent(self, account_id: str = None) -> str:
        """生成 User-Agent"""
        if not account_id:
            account_id = f"random_{random.randint(1, 999999)}"
        
        if account_id in self._user_agent_cache:
            return self._user_agent_cache[account_id]
        
        seed = int(hashlib.md5(account_id.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)
        
        chrome_versions = ["130.0.0.0", "131.0.0.0", "132.0.0.0"]
        user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{rng.choice(chrome_versions)} Safari/537.36"
        
        self._user_agent_cache[account_id] = user_agent
        return user_agent
    
    def _generate_session_id(self) -> str:
        """生成 sessionId"""
        return f";{int(time.time() * 1000)}"

    def _get_retry_reason(self, error: Exception) -> Optional[str]:
        """识别可重试错误"""
        error_text = str(error).lower()
        if "http 401" in error_text or "unauthenticated" in error_text:
            return "401 鉴权失败"
        if "recaptcha evaluation failed" in error_text:
            return "reCAPTCHA 验证失败"
        if "recaptcha" in error_text:
            return "reCAPTCHA 错误"
        if "http 403" in error_text:
            return "403 错误"
        if "http 429" in error_text or "too many requests" in error_text:
            return "429 限流"
        if "http 500" in error_text or "internal" in error_text:
            return "500 内部错误"
        return None

    async def _get_recaptcha_token(self, project_id: str, action: str = "IMAGE_GENERATION") -> Optional[str]:
        """根据配置获取 reCAPTCHA token"""
        method = (self.config.captcha.method or "").strip().lower()
        if method in {"", "none", "off", "disabled"}:
            return None
        if method == "personal":
            return await get_personal_recaptcha_token(
                project_id=project_id,
                action=action,
                st_token=self.config.token.st,
                headless=bool(self.config.captcha.personal_headless),
                timeout_seconds=int(self.config.captcha.personal_timeout),
                settle_seconds=float(self.config.captcha.personal_settle_seconds),
            )
        raise Exception(f"不支持的 captcha.method: {self.config.captcha.method}，仅支持 personal/none")
    
    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        use_st: bool = False,
        st_token: Optional[str] = None,
        use_at: bool = False,
        at_token: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """发送 HTTP 请求"""
        if headers is None:
            headers = {}
        else:
            headers = dict(headers)
        
        if use_st and st_token:
            headers["Cookie"] = f"__Secure-next-auth.session-token={st_token}"
        
        if use_at and at_token:
            headers["authorization"] = f"Bearer {at_token}"
        
        account_id = None
        if st_token:
            account_id = st_token[:16]
        elif at_token:
            account_id = at_token[:16]
        
        headers.update({
            "Content-Type": "application/json",
            "User-Agent": self._generate_user_agent(account_id)
        })
        
        for key, value in self._default_headers.items():
            headers.setdefault(key, value)
        
        request_timeout = timeout or self.config.flow.timeout
        
        if self.config.debug:
            print(f"[DEBUG] {method} {url}")
            if json_data:
                print(f"[DEBUG] Body: {json.dumps(json_data, ensure_ascii=False)[:500]}")
        
        try:
            if HAS_CURL_CFFI:
                async with AsyncSession() as session:
                    if method.upper() == "GET":
                        response = await session.get(
                            url, headers=headers, timeout=request_timeout, impersonate="chrome110"
                        )
                    else:
                        response = await session.post(
                            url, headers=headers, json=json_data, timeout=request_timeout, impersonate="chrome110"
                        )
                    
                    if response.status_code >= 400:
                        error_body = response.text[:500]
                        raise Exception(f"HTTP {response.status_code}: {error_body}")
                    
                    return response.json()
            else:
                async with aiohttp.ClientSession() as session:
                    if method.upper() == "GET":
                        async with session.get(
                            url, headers=headers, timeout=aiohttp.ClientTimeout(total=request_timeout)
                        ) as response:
                            if response.status >= 400:
                                error_body = await response.text()
                                raise Exception(f"HTTP {response.status}: {error_body[:500]}")
                            return await response.json()
                    else:
                        async with session.post(
                            url, headers=headers, json=json_data, timeout=aiohttp.ClientTimeout(total=request_timeout)
                        ) as response:
                            if response.status >= 400:
                                error_body = await response.text()
                                raise Exception(f"HTTP {response.status}: {error_body[:500]}")
                            return await response.json()
                            
        except Exception as e:
            raise Exception(f"请求失败: {str(e)}")
    
    async def st_to_at(self, st: str) -> Dict[str, Any]:
        """ST 转 AT"""
        url = f"{self.config.flow.labs_base_url}/auth/session"
        return await self._make_request(method="GET", url=url, use_st=True, st_token=st)

    async def refresh_at(self) -> str:
        """强制刷新 AT"""
        config = self.config
        if not config.token.st:
            raise Exception("未配置 Session Token (ST)，无法刷新 AT")

        result = await self.st_to_at(config.token.st)
        config.token.at = result.get("access_token", "")
        config.token.at_expires = result.get("expires", "")
        if "user" in result:
            config.token.user_paygate_tier = result["user"].get("userPaygateTier", config.token.user_paygate_tier)
        if not config.token.at:
            raise Exception("刷新 Access Token 失败")

        config.save_token()
        return config.token.at
    
    async def create_project(self, st: str, title: str = "Flow CLI Project") -> str:
        """创建项目"""
        url = f"{self.config.flow.labs_base_url}/trpc/project.createProject"
        json_data = {"json": {"projectTitle": title, "toolName": "PINHOLE"}}
        
        result = await self._make_request(
            method="POST", url=url, json_data=json_data, use_st=True, st_token=st
        )
        
        return result["result"]["data"]["json"]["result"]["projectId"]
    
    async def get_credits(self, at: str) -> Dict[str, Any]:
        """查询余额"""
        url = f"{self.config.flow.api_base_url}/credits"
        return await self._make_request(method="GET", url=url, use_at=True, at_token=at)
    
    def _detect_image_mime_type(self, image_bytes: bytes) -> str:
        """检测图片 MIME 类型"""
        if len(image_bytes) < 12:
            return "image/jpeg"
        if image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
            return "image/webp"
        if image_bytes[:4] == b'\x89PNG':
            return "image/png"
        if image_bytes[:3] == b'\xff\xd8\xff':
            return "image/jpeg"
        if image_bytes[:6] in (b'GIF87a', b'GIF89a'):
            return "image/gif"
        return "image/jpeg"
    
    async def upload_image(
        self, at: str, image_bytes: bytes, aspect_ratio: str = "IMAGE_ASPECT_RATIO_LANDSCAPE", project_id: Optional[str] = None
    ) -> str:
        """上传图片"""
        if aspect_ratio.startswith("VIDEO_"):
            aspect_ratio = aspect_ratio.replace("VIDEO_", "IMAGE_")
        
        mime_type = self._detect_image_mime_type(image_bytes)
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        ext = "png" if "png" in mime_type else "jpg"
        upload_file_name = f"flow_cli_upload_{int(time.time() * 1000)}.{ext}"
        
        url = f"{self.config.flow.api_base_url}/flow/uploadImage"
        
        client_context = {"tool": "PINHOLE"}
        if project_id:
            client_context["projectId"] = project_id
        
        json_data = {
            "clientContext": client_context,
            "fileName": upload_file_name,
            "imageBytes": image_base64,
            "isHidden": False,
            "isUserUploaded": True,
            "mimeType": mime_type
        }
        
        result = await self._make_request(
            method="POST", url=url, json_data=json_data, use_at=True, at_token=at
        )
        
        media_id = (
            result.get("media", {}).get("name")
            or result.get("mediaGenerationId", {}).get("mediaGenerationId")
        )
        
        if not media_id:
            raise Exception(f"上传响应缺少 media id: {list(result.keys())}")
        
        return media_id
    
    async def generate_image(
        self,
        at: str,
        project_id: str,
        prompt: str,
        model_name: str,
        aspect_ratio: str,
        image_inputs: Optional[List[Dict]] = None,
    ) -> Tuple[Dict[str, Any], str]:
        """生成图片"""
        url = f"{self.config.flow.api_base_url}/projects/{project_id}/flowMedia:batchGenerateImages"
        max_retries = max(1, int(self.config.flow.max_retries))
        last_error = None

        for retry_attempt in range(max_retries):
            recaptcha_token = await self._get_recaptcha_token(project_id=project_id, action="IMAGE_GENERATION")
            session_id = self._generate_session_id()
            client_context = {
                "sessionId": session_id,
                "projectId": project_id,
                "tool": "PINHOLE"
            }
            if recaptcha_token:
                client_context["recaptchaContext"] = {
                    "token": recaptcha_token,
                    "applicationType": "RECAPTCHA_APPLICATION_TYPE_WEB"
                }

            request_data = {
                "clientContext": client_context,
                "seed": random.randint(1, 999999),
                "imageModelName": model_name,
                "imageAspectRatio": aspect_ratio,
                "structuredPrompt": {"parts": [{"text": prompt}]},
                "imageInputs": image_inputs or []
            }

            json_data = {
                "clientContext": client_context,
                "mediaGenerationContext": {"batchId": str(uuid.uuid4())},
                "useNewMedia": True,
                "requests": [request_data]
            }

            try:
                result = await self._make_request(
                    method="POST",
                    url=url,
                    json_data=json_data,
                    use_at=True,
                    at_token=at,
                    timeout=self.config.flow.timeout,
                )
                return result, session_id
            except Exception as e:
                last_error = e
                reason = self._get_retry_reason(e)
                is_last_attempt = retry_attempt >= max_retries - 1
                if reason == "401 鉴权失败" and not is_last_attempt:
                    print("   提示: Access Token 失效，正在自动刷新...")
                    at = await self.refresh_at()
                    await asyncio.sleep(0.5)
                    continue
                if (not reason) or is_last_attempt:
                    raise
                print(f"   提示: {reason}，正在重试 ({retry_attempt + 2}/{max_retries})...")
                await asyncio.sleep(1)

        if last_error:
            raise last_error
        raise Exception("生成图片失败")

    async def upsample_image(
        self,
        at: str,
        project_id: str,
        media_id: str,
        target_resolution: str = "UPSAMPLE_IMAGE_RESOLUTION_2K",
        session_id: Optional[str] = None,
    ) -> str:
        """放大图片，返回 base64 编码图像"""
        url = f"{self.config.flow.api_base_url}/flow/upsampleImage"
        max_retries = max(1, int(self.config.flow.max_retries))
        last_error = None

        for retry_attempt in range(max_retries):
            recaptcha_token = await self._get_recaptcha_token(project_id=project_id, action="IMAGE_GENERATION")
            upsample_session_id = session_id or self._generate_session_id()

            client_context = {
                "sessionId": upsample_session_id,
                "projectId": project_id,
                "tool": "PINHOLE",
                "userPaygateTier": self.config.token.user_paygate_tier,
            }
            if recaptcha_token:
                client_context["recaptchaContext"] = {
                    "token": recaptcha_token,
                    "applicationType": "RECAPTCHA_APPLICATION_TYPE_WEB",
                }

            json_data = {
                "mediaId": media_id,
                "targetResolution": target_resolution,
                "clientContext": client_context,
            }

            try:
                result = await self._make_request(
                    method="POST",
                    url=url,
                    json_data=json_data,
                    use_at=True,
                    at_token=at,
                    timeout=max(self.config.flow.timeout, 300),
                )
                encoded = result.get("encodedImage", "")
                if not encoded:
                    raise Exception(f"放大响应缺少 encodedImage: {list(result.keys())}")
                return encoded
            except Exception as e:
                last_error = e
                reason = self._get_retry_reason(e)
                is_last_attempt = retry_attempt >= max_retries - 1
                if reason == "401 鉴权失败" and not is_last_attempt:
                    print("   提示: Access Token 失效，正在自动刷新...")
                    at = await self.refresh_at()
                    await asyncio.sleep(0.5)
                    continue
                if (not reason) or is_last_attempt:
                    raise
                print(f"   提示: {reason}，放大重试 ({retry_attempt + 2}/{max_retries})...")
                await asyncio.sleep(1)

        if last_error:
            raise last_error
        raise Exception("图片放大失败")
    
    async def ensure_valid_at(self) -> str:
        """确保 AT 有效"""
        config = self.config
        
        if not config.token.st:
            raise Exception("未配置 Session Token (ST)，请先运行 'flow-cli login' 登录")
        
        if config.token.at:
            return config.token.at
        
        print("正在获取 Access Token...")
        result = await self.st_to_at(config.token.st)
        
        config.token.at = result.get("access_token", "")
        config.token.at_expires = result.get("expires", "")
        
        if "user" in result:
            user_tier = result["user"].get("userPaygateTier", "PAYGATE_TIER_NOT_PAID")
            config.token.user_paygate_tier = user_tier
        
        if not config.token.at:
            raise Exception("获取 Access Token 失败")
        
        config.save_token()
        print("完成: Access Token 已获取并保存")
        
        return config.token.at
    
    async def ensure_project(self) -> str:
        """确保项目存在"""
        config = self.config
        
        if config.token.project_id:
            return config.token.project_id
        
        print("正在创建项目...")
        project_id = await self.create_project(config.token.st)
        
        config.token.project_id = project_id
        config.save_token()
        
        print(f"完成: 项目已创建: {project_id[:16]}...")
        
        return project_id


class ImageGenerator:
    """图片生成器"""
    
    def __init__(self):
        self.client = FlowClient()
        self.config = get_config()
    
    async def generate(
        self,
        prompt: str,
        model: str = None,
        reference_image: Optional[bytes] = None,
        output_path: Optional[str] = None,
        upscale: str = "none",
    ) -> str:
        """生成图片"""
        model = model or DEFAULT_MODEL
        model_config = get_model_config(model)
        
        print("\n开始生成图片")
        print(f"   模型: {model}")
        print(f"   提示词: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        
        at = await self.client.ensure_valid_at()
        project_id = await self.client.ensure_project()
        
        image_inputs = []
        if reference_image:
            print("   正在上传参考图片...")
            media_id = await self.client.upload_image(
                at=at,
                image_bytes=reference_image,
                aspect_ratio=model_config["aspect_ratio"],
                project_id=project_id
            )
            image_inputs.append({
                "name": media_id,
                "imageInputType": "IMAGE_INPUT_TYPE_REFERENCE"
            })
            print("   完成: 参考图片已上传")
        
        print("   正在生成图片...")
        result, session_id = await self.client.generate_image(
            at=at,
            project_id=project_id,
            prompt=prompt,
            model_name=model_config["model_name"],
            aspect_ratio=model_config["aspect_ratio"],
            image_inputs=image_inputs if image_inputs else None,
        )
        
        media = result.get("media", [])
        if not media:
            raise Exception("生成结果为空")
        
        image_url = media[0]["image"]["generatedImage"]["fifeUrl"]
        media_id = media[0].get("name")

        print("   完成: 图片生成成功")

        if upscale and upscale.lower() != "none":
            if not output_path:
                import time as _time
                suffix = upscale.lower()
                output_path = f"output/flow_{int(_time.time())}_{suffix}.png"

            if not media_id:
                print("   提示: 当前响应缺少 mediaId，无法放大，自动降级保存原图...")
                saved_path = await self._download_and_save(image_url, output_path)
                print(f"   完成: 已保底保存原图: {saved_path}")
                return saved_path

            target_resolution = (
                "UPSAMPLE_IMAGE_RESOLUTION_2K"
                if upscale.lower() == "2k"
                else "UPSAMPLE_IMAGE_RESOLUTION_4K"
            )
            print(f"   正在放大图片到 {upscale.upper()}...")
            try:
                encoded_image = await self.client.upsample_image(
                    at=at,
                    project_id=project_id,
                    media_id=media_id,
                    target_resolution=target_resolution,
                    session_id=session_id,
                )
                saved_path = self._save_base64_image(encoded_image, output_path)
                print(f"   完成: 已保存{upscale.upper()}图片: {saved_path}")
                return saved_path
            except Exception as upscale_error:
                print(f"   提示: {upscale.upper()}放大失败: {upscale_error}")
                print("   提示: 自动降级为原图并执行保底保存...")
                try:
                    saved_path = await self._download_and_save(image_url, output_path)
                    print(f"   完成: 已保底保存原图: {saved_path}")
                    return saved_path
                except Exception as save_error:
                    raise Exception(f"放大失败且原图保底保存失败: upscale={upscale_error}; save={save_error}")

        if output_path:
            saved_path = await self._download_and_save(image_url, output_path)
            print(f"   完成: 已保存到: {saved_path}")
            return saved_path

        return image_url
    
    async def _download_and_save(self, url: str, output_path: str) -> str:
        """下载并保存图片"""
        if HAS_CURL_CFFI:
            async with AsyncSession() as session:
                response = await session.get(url, timeout=60, impersonate="chrome110")
                image_data = response.content
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    image_data = await response.read()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "wb") as f:
            f.write(image_data)
        
        return str(output_file.absolute())

    def _save_base64_image(self, encoded_image: str, output_path: str) -> str:
        """保存 base64 图片到文件"""
        if "," in encoded_image and encoded_image.strip().startswith("data:image"):
            encoded_image = encoded_image.split(",", 1)[1]

        image_data = base64.b64decode(encoded_image)
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "wb") as f:
            f.write(image_data)

        return str(output_file.absolute())
    
    async def check_credits(self) -> Dict[str, Any]:
        """查询余额"""
        at = await self.client.ensure_valid_at()
        return await self.client.get_credits(at)

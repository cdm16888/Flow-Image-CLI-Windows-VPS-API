"""
Windows VPS browser reCAPTCHA token acquisition for personal mode.
Supports both LOCAL mode (Playwright on same machine) and REMOTE mode (HTTP call to browser gateway).

REMOTE MODE: Set environment variable FLOW_CAPTCHA_GATEWAY to the tunnel URL
             e.g. FLOW_CAPTCHA_GATEWAY="https://xxxx.trycloudflare.com"
"""

import os as _os
from typing import Optional

try:
    from playwright.async_api import async_playwright

    HAS_PLAYWRIGHT = True
except Exception:
    HAS_PLAYWRIGHT = False


RECAPTCHA_SITE_KEY = "6LdsFiUsAAAAAIjVDZcuLhaHiDn5nnHVXVRQGeMV"

# Remote gateway URL (set by environment variable)
_REMOTE_GATEWAY_URL = _os.environ.get("FLOW_CAPTCHA_GATEWAY", "").strip()


async def get_personal_recaptcha_token(
    project_id: str,
    action: str = "IMAGE_GENERATION",
    st_token: Optional[str] = None,
    headless: bool = False,
    timeout_seconds: int = 90,
    settle_seconds: float = 2.0,
) -> str:
    """Run reCAPTCHA in a windowsvps browser and return the token.

    Mode selection:
      - If FLOW_CAPTCHA_GATEWAY is set → HTTP call to remote browser gateway
      - Otherwise → windowsvps Playwright browser (original behavior)
    """
    # ── Remote gateway mode ────────────────────────────────────────────────
    if _REMOTE_GATEWAY_URL:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{_REMOTE_GATEWAY_URL}/recaptcha",
                json={
                    "project_id": project_id,
                    "action": action,
                    "settle_seconds": settle_seconds,
                },
                timeout=aiohttp.ClientTimeout(total=timeout_seconds),
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"Gateway recaptcha error {resp.status}: {text}")
                data = await resp.json()
                token = data.get("token", "")
                if not token:
                    raise Exception("Gateway returned empty reCAPTCHA token")
                return token

    # ── Windows VPS Playwright mode (original behavior) ─────────────────────────
    if not HAS_PLAYWRIGHT:
        raise Exception(
            "Playwright is not installed. Run: pip install playwright && python -m playwright install chromium"
        )

    url = f"https://labs.google/fx/tools/flow/project/{project_id}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-default-browser-check",
                "--disable-dev-shm-usage",
                "--no-proxy-server",
            ],
        )
        context = await browser.new_context(viewport={"width": 1440, "height": 900})

        try:
            page = await context.new_page()

            if st_token:
                await context.add_cookies(
                    [
                        {
                            "name": "__Secure-next-auth.session-token",
                            "value": st_token,
                            "domain": "labs.google",
                            "path": "/",
                            "httpOnly": True,
                            "secure": True,
                            "sameSite": "Lax",
                        }
                    ]
                )

            await page.goto(url, wait_until="domcontentloaded", timeout=timeout_seconds * 1000)
            await page.wait_for_timeout(int(max(0.0, settle_seconds) * 1000))

            await page.wait_for_function(
                "typeof grecaptcha !== 'undefined' && typeof grecaptcha.enterprise !== 'undefined' && typeof grecaptcha.enterprise.execute === 'function'",
                timeout=20000,
            )

            token = await page.evaluate(
                """
                async ({siteKey, actionName}) => {
                    return await new Promise((resolve, reject) => {
                        try {
                            grecaptcha.enterprise.ready(async () => {
                                try {
                                    const t = await grecaptcha.enterprise.execute(siteKey, {action: actionName});
                                    resolve(t || "");
                                } catch (err) {
                                    reject(err?.message || String(err));
                                }
                            });
                        } catch (err) {
                            reject(err?.message || String(err));
                        }
                    });
                }
                """,
                {"siteKey": RECAPTCHA_SITE_KEY, "actionName": action},
            )

            if not token:
                raise Exception("Browser execution succeeded but returned an empty token")
            return token
        finally:
            await context.close()
            await browser.close()

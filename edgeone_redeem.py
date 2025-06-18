"""EdgeOne 自动登录 → 获取 token → 兑换码流水线
===================================================
运行要求：
- Python ≥ 3.9
- pip install selenium selenium‑stealth requests
- 已正确安装 Chrome 与 chromedriver（路径已加入系统 PATH）

脚本流程：
1. 使用 Selenium 打开登录页，等待跳转完成并拿到 `skey` 与 `uin` cookie。
2. 用这些 cookie 向 TencentCloud 接口申请 `saas_token`（key）、`uin`、`ownerUin`。
3. 计算 `x‑csrfcode`，携带 cookie & csrf 调用 EdgeOne 兑换接口。
4. 打印兑换接口返回的结构化结果。

可在命令行直接运行：
    python edgeone_redeem.py YOUR_REDEEM_CODE
"""

from __future__ import annotations

import json
import random
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Dict, TypedDict

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth

###############################################################################
# 全局常量
###############################################################################
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
)
LOGIN_URL = (
    "https://edgeone.ai/login?"
    "s_url=https%3A%2F%2Fconsole.tencentcloud.com%2Fedgeone"
)
TOKEN_API = "https://www.tencentcloud.com/account/login/saas/getTokenFormSass"
REDEEM_API = "https://api.edgeone.ai/common/portal-user"
TIMEOUT = 30  # seconds

###############################################################################
# 类型声明
###############################################################################
class CookieResult(TypedDict):
    skey: str
    uin: str

class TokenResult(TypedDict):
    key: str
    uin: str
    ownerUin: str

###############################################################################
# Selenium 部分
###############################################################################

def launch_browser(headless: bool = False) -> webdriver.Chrome:
    """初始化 Chrome，并应用 selenium‑stealth"""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)

    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver


def get_skey_and_uin(login_url: str, timeout: int = TIMEOUT) -> CookieResult:
    """打开登录页，等待跳转完成并读取 `skey` 与 `uin` cookie"""
    driver = launch_browser(headless=False)
    try:
        driver.get(login_url)

        # 等待跳转发生
        WebDriverWait(driver, timeout).until(lambda d: d.current_url != login_url)
        # 等待页面完全加载
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        cookies = {
            c["name"]: urllib.parse.unquote(c["value"])
            for c in driver.get_cookies()
        }
        return {
            "skey": cookies.get("skey", ""),
            "uin": cookies.get("uin", ""),
        }
    finally:
        driver.quit()

###############################################################################
# HTTP 工具函数
###############################################################################

def build_token_url() -> str:
    """按规范构造 SaaS token API 的完整 URL"""
    params = {
        "platform": "intlSaaSTrtc",
        "random": "".join(random.choices("0123456789", k=6)),
        "s_url": "https://trtc.io",
        "clientUA": UA,
    }
    return f"{TOKEN_API}?{urllib.parse.urlencode(params)}"


def call_token_api(session: requests.Session, skey: str, uin: str) -> TokenResult:
    url = build_token_url()
    headers = {
        "Referer": "https://edgeone.ai/",
        "User-Agent": UA,
        "Cookie": f"uin={uin}; skey={skey};",
    }
    resp = session.get(url, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("code") != 0:
        raise RuntimeError(f"Token API error: {payload.get('msg')}")
    data = payload["data"]
    return {
        "key": data["key"],
        "uin": data["uin"],
        "ownerUin": str(data["ownerUin"]),
    }

###############################################################################
# 业务逻辑：兑换
###############################################################################

def djb2_hash(s: str) -> str:
    h = 5381
    for ch in s:
        h = h + (h << 5) + ord(ch)
    return str(h & 0x7FFFFFFF)


def redeem_code(session: requests.Session, token: TokenResult, code: str) -> dict:
    headers = {
        "Referer": "https://edgeone.ai/",
        "User-Agent": UA,
        "x-csrfcode": djb2_hash(token["key"]),
        "Cookie": (
            f"saas_uin={token['uin']}; "
            f"saas_ownerUin={token['ownerUin']}; "
            f"saas_token={token['key']}"
        ),
        "Content-Type": "application/json",
    }
    payload = {"Action": "redeem/consume", "Data": {"code": code}}
    resp = session.post(REDEEM_API, headers=headers, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()

###############################################################################
# CLI 入口
###############################################################################

def main(redeem_code_value: str):
    cookies = get_skey_and_uin(LOGIN_URL)
    if not all(cookies.values()):
        raise RuntimeError("未能获取 skey/uin cookie，请检查登录流程")

    skey = cookies["skey"]
    uin = cookies["uin"].lstrip("o")  # 移除前导 o

    with requests.Session() as session:
        token = call_token_api(session, skey, uin)
        result = redeem_code(session, token, redeem_code_value)
        print("\n🎯 兑换结果:\n", json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python edgeone_redeem.py <REDEEM_CODE>")
        sys.exit(1)
    main(sys.argv[1])

import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import webbrowser
import json
import time
import requests

# 导入你已有的功能逻辑（建议从模块 import，或粘贴整合）
from edgeone_redeem import get_skey_and_uin, call_token_api, redeem_code

# ========== 全局变量 ==========
token_info = {}  # 用于存储 key、uin、ownerUin

# ========== GUI 主窗口 ==========
window = tk.Tk()
window.title("EdgeOne 兑换工具")
window.geometry("600x500")

# ========== 左侧：兑换码输入框 ==========
tk.Label(window, text="兑换码").place(x=50, y=20)
entry_codes = tk.Text(window, width=30, height=12)
entry_codes.place(x=30, y=50)

# ========== 右侧：按钮与状态 ==========
tk.Label(window, text="当前状态:").place(x=300, y=20)
label_status = tk.Label(window, text="等待登录", fg="blue")
label_status.place(x=370, y=20)

# ========== 版权标志区域 ==========
def open_blog(event):
    webbrowser.open("https://blog.eswlnk.com")

copyright_label = tk.Label(window, text="Eswlnk Blog", fg="gray", cursor="hand2")
copyright_label.place(x=350, y=160)
copyright_label.bind("<Button-1>", open_blog)

# ========== 日志框 ==========
tk.Label(window, text="日志").place(x=30, y=280)
text_log = scrolledtext.ScrolledText(window, width=70, height=10)
text_log.place(x=30, y=310)

def log(msg: str):
    text_log.insert(tk.END, f"{msg}\n")
    text_log.see(tk.END)

# 初始免责声明与版权输出
log("⚠️ 本脚本仅供学习与个人使用，严禁用于任何商业或非法用途！")
log("📘 作者：Eswlnk Blog  https://blog.eswlnk.com")
log("🔓 本工具已开源，遵循 MIT 开源协议\n")

# ========== 获取登录信息按钮逻辑 ==========
def on_get_token():
    def task():
        try:
            label_status.config(text="正在登录...", fg="orange")
            cookies = get_skey_and_uin("https://edgeone.ai/login?s_url=https%3A%2F%2Fconsole.tencentcloud.com%2Fedgeone")
            if not cookies['skey'] or not cookies['uin']:
                raise Exception("未获取到 skey/uin")

            skey = cookies['skey']
            uin = cookies['uin'].lstrip('o')

            session = requests.Session()
            result = call_token_api(session, skey, uin)

            token_info.clear()
            token_info.update(result)

            label_status.config(text="✅ 成功获取相关 Token", fg="green")
            log("[Token] 获取成功")
        except Exception as e:
            label_status.config(text="❌ 登录失败", fg="red")
            log(f"[错误] 获取 token 失败：{e}")

    threading.Thread(target=task).start()

# ========== 兑换按钮逻辑 ==========
from concurrent.futures import ThreadPoolExecutor, as_completed

def on_redeem_all():
    def task():
        if not token_info:
            messagebox.showwarning("请先登录", "请先点击获取登录信息")
            return

        codes = entry_codes.get("1.0", tk.END).strip().split("\n")
        codes = [c.strip() for c in codes if c.strip()]
        session = requests.Session()

        def redeem_worker(code):
            try:
                result = redeem_code(session, token_info, code)
                data = result.get("data", {})
                status = data.get("code", "未知状态")
                message = data.get("message", "无说明")
                return f"[{code}] → {status} | {message}"
            except Exception as e:
                return f"[{code}] ❌ 异常: {e}"

        log(f"开始兑换 {len(codes)} 个码（每次最多并发 5 个）...\n")

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_code = {executor.submit(redeem_worker, code): code for code in codes}
            for future in as_completed(future_to_code):
                result = future.result()
                log(result)

    threading.Thread(target=task).start()

# ========== 按钮绑定 ==========
tk.Button(window, text="获取登录信息", width=18, command=on_get_token).place(x=350, y=60)
tk.Button(window, text="一键兑换", width=18, command=on_redeem_all).place(x=350, y=110)

# ========== 启动 GUI ==========
window.mainloop()

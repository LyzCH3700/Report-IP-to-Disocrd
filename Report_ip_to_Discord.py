import urllib.request
import json
import time
import os
from datetime import datetime

# 輸入你的Discord Webhook URL
WEBHOOK_URL = "URL"
REPORT_INTERVAL_SEC = 3600  # 每幾秒檢查一次

# 把 last_ip 記錄檔放在使用者家目錄底下
#BASE_DIR = os.path.expanduser("~")
#LAST_IP_FILE = os.path.join(BASE_DIR, "last_ip_discord.txt")


def get_public_ip():
    with urllib.request.urlopen("https://api.ipify.org?format=json") as resp:
        data = json.load(resp)
    return data["ip"]


def load_last_ip():
    if os.path.exists(LAST_IP_FILE):
        try:
            with open(LAST_IP_FILE, "r", encoding="utf-8") as f:
                return f.read().strip() or None
        except Exception as e:
            print("讀取 IP 記錄檔失敗：", repr(e))
    return None


def save_last_ip(ip: str):
    try:
        with open(LAST_IP_FILE, "w", encoding="utf-8") as f:
            f.write(ip)
        print("已更新 IP 記錄檔：", LAST_IP_FILE)
    except Exception as e:
        print("寫入 IP 記錄檔失敗：", repr(e))


def send_ip_to_discord(ip: str):
    date_str = datetime.now().strftime("%Y-%m-%d")
    content = f"[{date_str}]\n```{ip}```"

    payload = {"content": content}
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        WEBHOOK_URL,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "MyPythonDiscordWebhook/1.0",
        },
    )

    with urllib.request.urlopen(req) as resp:
        print("HTTP 狀態碼：", resp.status)
        print(f"已回報 IP：[{date_str}] {ip}")


if __name__ == "__main__":
    print("開始監控外網 IP 變化…")
    print("IP 記錄檔位置：", LAST_IP_FILE)

    last_ip = load_last_ip()
    if last_ip:
        print("上次記錄的 IP：", last_ip)
    else:
        print("尚無歷史 IP 記錄，首次會直接回報。")

    while True:
        try:
            current_ip = get_public_ip()
            print("目前 IP：", current_ip)

            if current_ip != last_ip:
                print("偵測到 IP 變更，準備回報 Discord。")
                send_ip_to_discord(current_ip)
                save_last_ip(current_ip)
                last_ip = current_ip
            else:
                print("IP 未變更，本次不回報。")

        except Exception as e:
            print("發生錯誤：", repr(e))

        time.sleep(REPORT_INTERVAL_SEC)

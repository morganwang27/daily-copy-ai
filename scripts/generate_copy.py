import os
import json
import time
from datetime import datetime, timezone, timedelta

import requests


# 台灣時間
tz = timezone(timedelta(hours=8))
today = datetime.now(tz).strftime("%Y-%m-%d")


API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise Exception("GEMINI_API_KEY not found")


# ✅ 先定義 url（你目前就是少了這段或順序錯）
MODEL = "gemini-2.0-flash"
url = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODEL}:generateContent"
    f"?key={API_KEY}"
)


prompt = f"""
你是一位短影音文案專家。

請幫我產生一支 15 秒短影音的「完整文案」。

主題：AI 自動幫我每天產內容  
平台：Reels / TikTok / Shorts  
語氣：簡單、有梗、行動導向  

請用以下格式輸出（中文）：
1. Hook（第一句超吸睛）
2. 口播稿（3～5 句）
3. CTA（行動呼籲）
"""


payload = {
    "contents": [
        {
            "parts": [{"text": prompt}]
        }
    ]
}


def call_gemini_with_retry(_url, _payload, max_retries=6):
    for attempt in range(max_retries):
        res = requests.post(
            _url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(_payload),
            timeout=60,
        )

        # 成功
        if res.status_code == 200:
            return res

        # 429 / 503：重試（指數退避 + 小抖動）
        if res.status_code in (429, 503):
            wait = (2 ** attempt) + (attempt * 0.5)
            print(f"Retryable error {res.status_code}. Waiting {wait:.1f}s...")
            time.sleep(wait)
            continue

        # 其他錯誤直接拋出
        print("Non-retryable error:", res.status_code, res.text)
        res.raise_for_status()

    raise Exception(f"Failed after retries. Last status: {res.status_code} body={res.text}")


res = call_gemini_with_retry(url, payload)
text = res.json()["candidates"][0]["content"]["parts"][0]["text"]

# 輸出成檔案
os.makedirs("outputs", exist_ok=True)
path = f"outputs/{today}.md"

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Generated copy saved to {path}")

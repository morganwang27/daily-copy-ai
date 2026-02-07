import os
from datetime import datetime, timezone, timedelta
import requests
import json

# 台灣時間
tz = timezone(timedelta(hours=8))
today = datetime.now(tz).strftime("%Y-%m-%d")

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise Exception("GEMINI_API_KEY not found")

url = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
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
            "parts": [
                {"text": prompt}
            ]
        }
    ]
}

res = requests.post(
    url,
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload)
)

res.raise_for_status()
text = res.json()["candidates"][0]["content"]["parts"][0]["text"]

# 輸出成檔案（之後你可改成寫 Google Sheet）
os.makedirs("outputs", exist_ok=True)
path = f"outputs/{today}.md"

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Generated copy saved to {path}")

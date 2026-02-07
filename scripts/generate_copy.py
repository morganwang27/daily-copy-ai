import os
import json
import requests
from datetime import datetime, timezone, timedelta

# 台灣時間
tz = timezone(timedelta(hours=8))
today = datetime.now(tz).strftime("%Y-%m-%d")

PROMPT = f"""
你是一位短影音文案專家。
請產生一支 15 秒短影音的完整文案（適用 Reels / TikTok / Shorts）。

主題：AI 每天自動幫我產內容（日期：{today}）
語氣：簡單、有梗、1句就抓住注意力
請用以下格式輸出（用繁中）：
1) Hook（第一句超吸睛）
2) 內容（3-5 句，節奏快）
3) CTA（引導留言/追蹤）
4) Hashtags（8-12 個）
"""

def call_openai():
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=PROMPT,
    )
    return resp.output_text.strip()

def call_cloudflare():
    account_id = os.environ["CF_ACCOUNT_ID"]
    token = os.environ["CF_API_TOKEN"]
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/meta/llama-3-8b-instruct"

    payload = {
        "messages": [
            {"role": "system", "content": "你是一位短影音文案專家，請用繁體中文輸出。"},
            {"role": "user", "content": PROMPT},
        ]
    }

    r = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    # Cloudflare 回傳通常在 result.response
    return data["result"]["response"].strip()

def main():
    text = None
    used = None

    # 先嘗試 OpenAI（如果你有 quota 就會用 OpenAI）
    try:
        text = call_openai()
        used = "openai"
    except Exception as e:
        print(f"[warn] OpenAI failed: {e}")

    # OpenAI 不行就改用 Cloudflare（免費）
    if not text:
        text = call_cloudflare()
        used = "cloudflare"

    os.makedirs("output", exist_ok=True)
    out_path = f"output/{today}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Daily Copy ({today})\n\n")
        f.write(f"_generated_by: {used}_\n\n")
        f.write(text + "\n")

    print(f"[ok] wrote {out_path} ({used})")

if __name__ == "__main__":
    main()

import os
from datetime import datetime, timezone, timedelta
from openai import OpenAI

# 台灣時間
tz = timezone(timedelta(hours=8))
today = datetime.now(tz).strftime("%Y-%m-%d")

# 讀取 GitHub Secrets 裡的 API Key
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

prompt = """
你是一位短影音文案企劃。
請幫我產生「一支 15 秒短影音」的完整文案。

主題：AI 自動幫我每天產內容
平台：Reels / TikTok / Shorts
語氣：簡單、有梗、行動導向

請用以下格式輸出：
1. Hook（第一句超吸睛）
2. 口播腳本（逐句）
3. 畫面建議（對應口播）
4. CTA（引導追蹤或留言）
5. Hashtags（10 個）

限制：
- 不要提到你是 AI
- 不要出現品牌名稱
"""

response = client.responses.create(
    model="gpt-4o-mini",
    input=prompt
)

text = response.output_text

# 把結果存成檔案，給 GitHub commit
os.makedirs("outputs", exist_ok=True)
filename = f"outputs/{today}.md"

with open(filename, "w", encoding="utf-8") as f:
    f.write(f"# {today} 文案\n\n")
    f.write(text)

print(f"Saved to {filename}")

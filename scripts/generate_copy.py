import time

def call_gemini_with_retry(url, payload, max_retries=6):
    for attempt in range(max_retries):
        res = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=60,
        )

        # 成功
        if res.status_code == 200:
            return res

        # 429 / 503 之類：重試（指數退避 + 抖動）
        if res.status_code in (429, 503):
            wait = (2 ** attempt) + (attempt * 0.5)
            print(f"Retryable error {res.status_code}. Waiting {wait:.1f}s...")
            time.sleep(wait)
            continue

        # 其他錯誤直接拋出
        res.raise_for_status()

    raise Exception(f"Failed after retries. Last status: {res.status_code} body={res.text}")

res = call_gemini_with_retry(url, payload)
text = res.json()["candidates"][0]["content"]["parts"][0]["text"]

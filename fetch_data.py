import requests
import json
import os
import time
import urllib3

# 停用因為 verify=False 而產生的 InsecureRequestWarning 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 從 App.vue 取得的 API URL
API_URL = 'https://data.taipei/api/v1/dataset/8e11e7c2-9c8d-4143-a557-11997fdab5fa?scope=resourceAquire'
# CKAN API 通常的單次請求上限是 1000
LIMIT = 1000
# 輸出路徑，對應 Vue 的 public 資料夾
OUTPUT_PATH = 'public/1999_data.json'

def fetch_all_data():
    """
    從台北市 1999 案件 API 完整抓取所有資料，並儲存為一個 JSON 檔案。
    """
    all_records = []
    offset = 0
    total = None

    print(">>> 開始抓取全量派工數據...")

    while True:
        try:
            # 組合分頁請求的 URL
            url = f"{API_URL}&limit={LIMIT}&offset={offset}"
            print(f"正在請求: {url}")
            
            # 加入 verify=False 忽略 SSL 憑證驗證，解決政府網站憑證不受信任的問題
            response = requests.get(url, timeout=60, verify=False)
            response.raise_for_status()  # 如果回應狀態碼是 4xx 或 5xx，則拋出異常
            
            data = response.json()
            
            if not data or 'result' not in data:
                print("錯誤：收到的資料結構無效。")
                break

            results = data['result'].get('results', [])
            if not results:
                print("已無更多資料，抓取完成。")
                break
            
            all_records.extend(results)

            if total is None:
                total = data['result'].get('count', 0)
                print(f"--- 資料總筆數: {total} ---")

            print(f"已抓取 {len(results)} 筆，目前累計: {len(all_records)} / {total}")

            offset += LIMIT
            
            if total > 0 and len(all_records) >= total:
                print("已抓取所有資料。")
                break

            time.sleep(1) # 禮貌性延遲，避免對伺服器造成過大壓力

        except requests.exceptions.RequestException as e:
            print(f"請求發生錯誤: {e}，5 秒後重試...")
            time.sleep(5)
            continue

    print(f"\n>>> 成功抓取總計 {len(all_records)} 筆資料。")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_records, f, ensure_ascii=False)
    print(f"✅ 資料已成功儲存至 {OUTPUT_PATH}")

if __name__ == "__main__":
    fetch_all_data()
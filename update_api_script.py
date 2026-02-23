import re
import os
from playwright.sync_api import sync_playwright

# 目標資料集頁面 (臺北市 1999 派工數據)
DATASET_URL = "https://data.taipei/dataset/detail?id=b796f87a-0ed8-4e57-89f6-225a4941b1ed"

def fetch_latest_id():
    print("正在啟動 Playwright 瀏覽器...")
    with sync_playwright() as p:
        # GitHub Actions 環境必須使用 headless=True
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print(f"前往頁面: {DATASET_URL}")
            page.goto(DATASET_URL)
            
            # [新增] 等待網路狀態穩定 (避免頁面還沒載入完就執行)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except:
                print("等待網路閒置超時，繼續嘗試...")

            # 嘗試關閉可能出現的 API 說明對話框
            try:
                # 使用 click 帶 timeout 來自動等待元素出現 (最多等 3 秒)
                page.locator("#close-api-dialog-0").click(timeout=3000)
                print("已關閉 API 對話框")
            except Exception:
                pass # 忽略對話框錯誤，繼續執行

            # 策略 1: 嘗試透過 UI 定位獲取 (優先)
            try:
                api_cell = page.get_by_role("cell", name="https://data.taipei/api/v1/").first
                # [修正] 顯式等待元素可見，最多等 5 秒
                api_cell.wait_for(state="visible", timeout=5000)
                
                url_text = api_cell.inner_text()
                print(f"UI 定位找到文字: {url_text}")
                
                match = re.search(r'dataset/([a-f0-9-]{36})', url_text)
                if match:
                    new_id = match.group(1)
                    print(f"UI 解析成功！最新 ID 為: {new_id}")
                    return new_id
            except Exception as e:
                print(f"UI 定位解析失敗，轉為搜尋原始碼... ({e})")
            
            # 策略 2: 全頁原始碼暴力搜尋 (備案)
            # 直接在 HTML 中搜尋 "api/v1/dataset/{UUID}" 格式
            content = page.content()
            match = re.search(r'api/v1/dataset/([a-f0-9-]{36})', content)
            if match:
                new_id = match.group(1)
                print(f"原始碼解析成功！最新 ID 為: {new_id}")
                return new_id

            print("無法從頁面中解析出有效的 API ID")
            return None

        except Exception as e:
            print(f"Playwright 執行錯誤: {e}")
            return None
        finally:
            browser.close()

def update_app_vue(new_id):
    # 更新 App.vue
    file_path = 'App.vue'
    if not os.path.exists(file_path):
        print(f"錯誤：找不到 {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 比對 App.vue 中的 API_URL 定義
    # const API_URL = '.../dataset/UUID?scope...';
    pattern = r'(dataset\/)([a-f0-9-]{36})(\?scope)'
    
    # 檢查並更新
    current_match = re.search(pattern, content)
    if current_match:
        old_id = current_match.group(2)
        if old_id == new_id:
            print("目前的 ID 已是最新，無需更新。")
            return False # 代表無變動
        
        # 執行替換
        new_content = re.sub(pattern, fr'\g<1>{new_id}\g<3>', content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"更新成功：{old_id} -> {new_id}")
        return True
    else:
        print("在 App.vue 中找不到符合格式的 API 連結。")
        return False

if __name__ == "__main__":
    latest_id = fetch_latest_id()
    if latest_id:
        update_app_vue(latest_id)

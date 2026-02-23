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
            
            # 嘗試關閉可能出現的 API 說明對話框
            try:
                close_btn = page.locator("#close-api-dialog-0")
                if close_btn.is_visible(timeout=5000):
                    close_btn.click()
                    print("已關閉 API 對話框")
            except Exception:
                pass # 忽略對話框錯誤，繼續執行

            # 尋找包含 API URL 的儲存格
            # 使用者提供的定位器: page.get_by_role("cell", name="https://data.taipei/api/v1/")
            api_cell = page.get_by_role("cell", name="https://data.taipei/api/v1/").first
            
            if api_cell.is_visible():
                url_text = api_cell.inner_text()
                print(f"找到 API URL 文字: {url_text}")
                
                # 提取 UUID (格式: .../dataset/{UUID}?scope...)
                match = re.search(r'dataset/([a-f0-9-]{36})', url_text)
                if match:
                    new_id = match.group(1)
                    print(f"解析成功！最新 ID 為: {new_id}")
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

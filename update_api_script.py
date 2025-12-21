import requests
import re
import os

# 優化後的 API 檢索網址 (排除 UI 參數，直接請求 JSON 數據)
# 搜尋關鍵字：臺北市政府1999派工資料
SEARCH_API = "https://data.taipei/api/v1/dataset/search?q=%E8%87%BA%E5%8C%97%E5%B8%82%E6%94%BF%E5%BA%9C1999%E6%B4%BE%E5%B7%A5%E8%B3%87%E6%96%99"

def fetch_latest_id():
    try:
        print(f"正在從資料平台檢索最新 ID...")
        response = requests.get(SEARCH_API, timeout=30)
        data = response.json()
        
        # 尋找結果列表
        results = data.get('result', {}).get('results', [])
        
        if results:
            # 取得搜尋結果中的第一個資料集 ID
            latest_id = results[0].get('id')
            dataset_title = results[0].get('title', '未知名稱')
            print(f"搜尋成功！找到資料集：{dataset_title}")
            print(f"最新 ID 為: {latest_id}")
            return latest_id
        else:
            print("搜尋不到匹配的資料集。")
    except Exception as e:
        print(f"搜尋過程發生錯誤: {e}")
    return None

def update_html_file(new_id):
    # 確保對接您的 index.html (原檔名 1999_11411.html)
    file_path = 'index.html' 
    if not os.path.exists(file_path):
        print(f"錯誤：找不到 {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 比對原始代碼中的 API_BASE_URL 結構
    # 格式為 dataset/UUID?scope
    pattern = r'dataset\/([a-f0-9-]{36})\?scope'
    
    # 檢查是否需要更新
    current_match = re.search(pattern, content)
    if current_match:
        old_id = current_match.group(1)
        if old_id == new_id:
            print("目前的 ID 已是最新，無需更新。")
            return False # 代表無變動
        
        # 執行替換
        new_content = re.sub(pattern, f'dataset/{new_id}?scope', content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"更新成功：{old_id} -> {new_id}")
        return True
    else:
        print("在 HTML 中找不到符合格式的 API 連結。")
        return False

if __name__ == "__main__":
    latest_id = fetch_latest_id()
    if latest_id:
        if not update_html_file(latest_id):
            # 如果沒有變動，確保工作流程結束
            print("檔案內容無須變更。")

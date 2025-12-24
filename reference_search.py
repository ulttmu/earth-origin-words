"""
參考圖搜尋系統 - earthorigin style 344張圖片
"""
import json
import os
from pathlib import Path
from typing import List, Tuple
import re

# 路徑設定
INDEX_PATH = "/Users/yuan/comfyui_tools/reference_index.json"
DATASET_PATH = "/Users/yuan/Downloads/pinterest-downloads/earthorigin-lora/_processed"
GDRIVE_URL = "https://drive.google.com/drive/folders/174dhecRBd4R2GBF47cztuGmcgxcIBo_W"

# 載入索引
def load_index():
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

INDEX = load_index()


def search(query: str, top_k: int = 5) -> List[dict]:
    """
    搜尋最相關的參考圖

    Args:
        query: 搜尋關鍵詞，如 "soap herbs natural" 或 "閱讀 書本 溫暖"
        top_k: 返回數量

    Returns:
        [{"filename": "xxx.jpg", "caption": "...", "score": 0.8, "path": "..."}, ...]
    """
    # 處理查詢詞
    query_words = set(query.lower().replace(',', ' ').split())

    # 中文關鍵詞映射
    zh_en_map = {
        '閱讀': ['reading', 'book', 'journal'],
        '書': ['book', 'journal', 'reading'],
        '植物': ['plant', 'botanical', 'leaf', 'herb', 'flower'],
        '葉子': ['leaf', 'leaves', 'botanical'],
        '花': ['flower', 'floral', 'botanical'],
        '手': ['hand', 'hands', 'holding'],
        '皂': ['soap', 'bar'],
        '肥皂': ['soap', 'bar', 'handmade'],
        '自然': ['natural', 'nature', 'organic'],
        '溫暖': ['warm', 'cozy', 'soft'],
        '光線': ['light', 'sunlight', 'window'],
        '人物': ['woman', 'person', 'portrait', 'human'],
        '特寫': ['close-up', 'detail', 'macro'],
        '產品': ['product', 'soap', 'bar'],
        '白色背景': ['white background', 'minimal'],
        '木頭': ['wood', 'wooden'],
        '陶瓷': ['ceramic', 'pottery'],
        '茶': ['tea', 'cup'],
        '咖啡': ['coffee', 'cup'],
        '早晨': ['morning', 'dawn', 'sunrise'],
        '黃昏': ['evening', 'sunset', 'dusk'],
        '冬天': ['winter', 'cold', 'snow'],
        '夏天': ['summer', 'warm', 'sun'],
        '秋天': ['autumn', 'fall', 'harvest'],
        '春天': ['spring', 'bloom', 'fresh'],
    }

    # 擴展中文查詢
    expanded_query = set(query_words)
    for zh, en_list in zh_en_map.items():
        if zh in query:
            expanded_query.update(en_list)

    results = []
    for img in INDEX["images"]:
        caption_lower = img["caption"].lower()
        keywords = set(img.get("keywords", []))

        # 計算匹配分數
        score = 0
        matched_words = []

        for word in expanded_query:
            if word in caption_lower:
                score += 1
                matched_words.append(word)
            elif any(word in kw for kw in keywords):
                score += 0.5
                matched_words.append(word)

        if score > 0:
            results.append({
                "filename": img["filename"],
                "caption": img["caption"],
                "score": score,
                "matched": matched_words,
                "path": os.path.join(DATASET_PATH, img["filename"])
            })

    # 排序並返回
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def search_by_category(category: str) -> List[dict]:
    """
    按類別搜尋

    類別:
    - 人物: woman, person, portrait
    - 植物: plant, botanical, leaf, flower
    - 產品: soap, product, bar
    - 場景: interior, room, space
    - 細節: close-up, detail, texture
    - 手部: hand, hands, holding
    """
    category_keywords = {
        "人物": ["woman", "person", "portrait", "human", "face"],
        "植物": ["plant", "botanical", "leaf", "flower", "herb", "leaves"],
        "產品": ["soap", "product", "bar", "bottle"],
        "場景": ["interior", "room", "space", "window", "kitchen"],
        "細節": ["close-up", "detail", "texture", "macro"],
        "手部": ["hand", "hands", "holding", "fingers"],
        "書籍": ["book", "journal", "reading", "writing"],
        "食物": ["food", "tea", "coffee", "cup", "bowl"],
        "自然": ["nature", "outdoor", "garden", "stone", "water"],
    }

    keywords = category_keywords.get(category, [category])
    query = " ".join(keywords)
    return search(query, top_k=20)


def get_random(n: int = 5) -> List[dict]:
    """隨機獲取 n 張參考圖"""
    import random
    samples = random.sample(INDEX["images"], min(n, len(INDEX["images"])))
    return [{
        "filename": img["filename"],
        "caption": img["caption"],
        "path": os.path.join(DATASET_PATH, img["filename"])
    } for img in samples]


def get_stats() -> dict:
    """獲取統計資訊"""
    # 分析打標內容
    all_words = []
    for img in INDEX["images"]:
        words = img["caption"].lower().replace(',', ' ').split()
        all_words.extend(words)

    from collections import Counter
    word_freq = Counter(all_words)

    return {
        "total_images": INDEX["total_images"],
        "total_captions": INDEX["total_captions"],
        "top_keywords": word_freq.most_common(30),
        "dataset_path": DATASET_PATH,
        "gdrive_url": GDRIVE_URL
    }


if __name__ == "__main__":
    print("=== 參考圖搜尋系統 ===\n")

    # 顯示統計
    stats = get_stats()
    print(f"總圖片數: {stats['total_images']}")
    print(f"有打標數: {stats['total_captions']}")
    print(f"\n常見關鍵詞: {[w for w, c in stats['top_keywords'][:10]]}")

    # 測試搜尋
    print("\n\n=== 搜尋測試 ===")

    test_queries = [
        "soap herbs natural",
        "book reading warm",
        "植物 葉子",
        "手 特寫",
        "woman portrait"
    ]

    for query in test_queries:
        print(f"\n搜尋: '{query}'")
        results = search(query, top_k=3)
        for r in results:
            print(f"  [{r['score']:.1f}] {r['filename']}: {r['caption'][:60]}...")

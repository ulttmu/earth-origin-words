# Z-Image Edit 產品合成 Workflow 設置指南

## 📦 Workflow 已上傳

位置：`C:\Users\user\Desktop\product_placement_workflow.json`

## 🎯 Workflow 功能

**用途**：將產品圖（洗髮精瓶）自然合成到場景圖（侘寂風木架）

**輸入**：
1. 場景圖（要保留的背景）
2. 產品圖（要放進去的物品）
3. 遮罩（塗改想放產品的位置）

**輸出**：
- 自然融合的合成圖
- 自動匹配光照和風格

## 🚀 使用步驟

### 1. 在 ComfyUI 載入 Workflow

```
1. 開啟瀏覽器：http://localhost:8188
2. 拖放 product_placement_workflow.json 到 ComfyUI
3. 或點擊 Load 按鈕選擇文件
```

### 2. 準備圖片

```
將以下圖片放到：C:\ComfyUI\input\

- scene.png    (場景圖 - 侘寂風木架)
- product.png  (產品圖 - 洗髮精瓶)
```

### 3. 設置節點

```
節點 1 - 場景圖:
  選擇 scene.png

節點 2 - 產品圖:
  選擇 product.png

節點 3 - Mask Editor:
  在場景圖上塗改想放產品的位置
  （塗白色 = 要編輯的區域）

節點 4 - Z-Image Edit:
  Prompt: "place shampoo bottle naturally on wooden shelf, match warm lighting"
  Strength: 0.8 (保留場景程度)
  Reference Strength: 0.85 (參考產品圖程度)
```

### 4. 執行生成

```
點擊 "Queue Prompt" 按鈕
等待 10-30 秒生成
結果會出現在右側預覽
```

## ⚙️ 參數調整

### Strength (強度)
- **0.7**: 大幅改變場景
- **0.8**: 平衡（推薦）
- **0.9**: 保留更多場景細節

### Reference Strength (參考強度)
- **0.7**: 產品外觀變化較大
- **0.85**: 平衡（推薦）
- **0.95**: 嚴格保持產品外觀

### Guidance Scale (引導強度)
- **5.0**: 更自由創作
- **7.0**: 平衡（推薦）
- **10.0**: 嚴格遵循 prompt

### Steps (步數)
- **15**: 快速測試
- **20**: 標準品質（推薦）
- **30**: 高品質（較慢）

## 🎨 Prompt 範例

### 基礎版
```
place product naturally on shelf, match lighting
```

### 詳細版
```
place earth origin shampoo bottle on wooden shelf among natural items, warm ambient lighting, rustic wabi-sabi style, natural shadows
```

### 特定位置
```
place bottle on middle shelf between ceramic jar and towels, soft natural light from left
```

## 🔧 如果節點找不到

workflow 可能需要調整節點名稱。請執行以下 Python 腳本查看可用的 Z-Image 節點：

```python
import os
import sys
sys.path.append('C:/ComfyUI')
import nodes

# 列出所有包含 'zimage' 的節點
for name in nodes.NODE_CLASS_MAPPINGS.keys():
    if 'zimage' in name.lower() or 'z-image' in name.lower():
        print(f"Found: {name}")
```

## 📝 常見問題

### Q: 產品看起來不自然？
A: 降低 strength 到 0.7，增加 reference_strength 到 0.9

### Q: 產品變形了？
A: 增加 reference_strength 到 0.95，或使用 ControlNet

### Q: 光照不匹配？
A: 在 prompt 中詳細描述場景光照：
   "soft warm lighting from upper left, natural shadows"

### Q: 生成太慢？
A: 降低 steps 到 15，或減小圖片尺寸

## 🎯 測試建議

1. **先用低參數快速測試**：steps=15, size=512
2. **調整 prompt 和位置**：找到最佳構圖
3. **提高品質**：steps=25, size=768
4. **批次處理**：滿意後用相同設置處理多張

## 📊 批次處理

如果要處理多張產品圖，可以：

```python
# 批次處理腳本（待創建）
# 自動載入多張產品圖
# 使用相同場景和設置
# 批次生成
```

---

**下一步**：請在 ComfyUI 中測試 workflow，如果有任何節點錯誤或需要調整，告訴我具體的錯誤訊息。

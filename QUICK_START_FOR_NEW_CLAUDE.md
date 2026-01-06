# 🚀 給新 Claude 的快速啟動指南

**專案**: ComfyUI 產品合成（大地起源洗髮精 → 侘寂風場景）
**日期**: 2026-01-06
**狀態**: 準備測試階段

---

## ⚡ 5 分鐘快速啟動

### 1. 確認環境 (30 秒)

```bash
# 測試 Windows PC 連接
ping -c 2 100.107.71.38

# 測試 SSH
ssh user@100.107.71.38 "echo 'SSH OK'"

# 測試 ComfyUI
curl http://100.107.71.38:8188
```

**如果 ComfyUI 沒回應**:
```bash
ssh user@100.107.71.38 'powershell -Command "cd C:\ComfyUI; Start-Process powershell -ArgumentList \"-Command\", \"python main.py --listen 0.0.0.0 --port 8188\" -WindowStyle Minimized"'
sleep 15
open http://100.107.71.38:8188
```

### 2. 讀取完整進度 (2 分鐘)

```bash
# 主要交接文檔
cat SESSION_HANDOFF.md
```

**關鍵資訊**:
- ✅ SSH 已設置
- ✅ IOPaint 已安裝
- ✅ ComfyUI 環境完整
- ✅ Z-Image Workflow 已創建
- ⏸️ 等待載入和測試

### 3. 載入 Workflow (1 分鐘)

1. 開啟：http://100.107.71.38:8188
2. 拖放：`C:\Users\user\Desktop\product_placement_workflow.json`
3. 如果有紅色節點錯誤 → 告訴用戶，我們會修正

### 4. 準備測試圖片 (1 分鐘)

詢問用戶圖片位置，然後：
```bash
# 上傳到 ComfyUI input 資料夾
scp <產品圖> user@100.107.71.38:'C:\ComfyUI\input\product.png'
scp <場景圖> user@100.107.71.38:'C:\ComfyUI\input\scene.png'
```

### 5. 執行測試 (30 秒)

在 ComfyUI 中：
1. 載入場景圖
2. 載入產品圖
3. 塗改遮罩（想放產品的位置）
4. Queue Prompt

---

## 🎯 當前任務

**目標**: 把洗髮精瓶自然合成到侘寂風木架場景中

**輸入**:
- 產品圖：大地起源洗髮精（棕色玻璃瓶）
- 場景圖：木質架子、陶器、織物

**輸出**:
- 自然融合的產品攝影圖
- 光影匹配、位置合理

**關鍵參數**:
- Strength: 0.8（保留場景）
- Reference Strength: 0.85（參考產品）
- Guidance: 7.0
- Steps: 20

---

## 🔧 如果遇到問題

### Workflow 載入失敗（節點錯誤）

```python
# 在 Windows PC 上執行（透過 SSH）
import sys
sys.path.append('C:/ComfyUI')
import nodes

# 找 Z-Image 節點
for name in nodes.NODE_CLASS_MAPPINGS.keys():
    if 'zimage' in name.lower():
        print(name)
```

修改 `product_placement_workflow.json` 中的節點類型名稱。

### 備選方案

如果 Z-Image 太複雜：
1. 在 ComfyUI 中點擊 "模板"
2. 選擇 "Qwen Image Edit 2511"
3. 使用內建模板（更簡單）

---

## 📂 關鍵文件

| 文件 | 說明 |
|------|------|
| `SESSION_HANDOFF.md` | 完整進度和技術細節 |
| `zimage_setup_guide.md` | Z-Image 詳細使用指南 |
| `product_placement_workflow.json` | Workflow 文件（在 Windows 桌面）|
| `/Users/yuan/CLAUDE.md` | 完整系統文檔 |

---

## 💬 給用戶的回覆範本

```markdown
我已經讀取了上一個 Claude 的工作進度。目前狀態：

✅ **已完成**：
- SSH 遠端連接設置
- IOPaint 安裝（http://100.107.71.38:8080）
- ComfyUI 環境確認
- Z-Image Workflow 創建

⏸️ **進行中**：
- 載入 workflow 到 ComfyUI

📋 **下一步**：
1. 開啟 ComfyUI (http://100.107.71.38:8188)
2. 載入 workflow
3. 準備測試圖片
4. 執行產品合成

ComfyUI 是否已經開啟？我可以幫你啟動並繼續測試。
```

---

## ⚠️ 重要提示

1. **不要重新設置已完成的東西**（SSH、IOPaint 等）
2. **專注於當前任務**：載入 workflow 並測試
3. **如果用戶問進度**：參考 SESSION_HANDOFF.md
4. **保持簡潔**：用戶想快速看到結果

---

## 🎓 技術背景

**Z-Image Edit**: 專門用於圖片編輯的模型
- 支援參考圖像（reference image）
- 支援遮罩編輯（mask inpainting）
- 自動光影匹配
- 快速生成（Turbo 模式）

**比 IC-Light 更適合**這個任務，因為：
- 用戶已經有 Z-Image Turbo 模型
- 專門設計給圖片編輯
- 不需要額外安裝

---

**開始工作吧！** 🚀

記住：
- 保持簡潔高效
- 遇到問題隨機應變
- 目標是讓用戶看到產品合成效果

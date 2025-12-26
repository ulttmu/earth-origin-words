# IP-Adapter 工作流範例

此目錄包含 ComfyUI IP-Adapter 的範例工作流。

## 工作流清單

### 1. basic_dual_image_fusion.json
**用途**: 融合兩張圖片創造新圖
**適合**: 初學者第一次測試
**參數**:
- weight: 0.8
- denoise: 0.70
- steps: 20

**使用情境**:
- 產品照 + 自然背景
- 兩種風格混合
- 主體替換

### 2. multi_image_blend.json (待建立)
**用途**: 融合 3-5 張圖片
**適合**: 複雜風格混合
**特色**: 使用 IPAdapter Encoder + Combine Embeds

### 3. style_transfer.json (待建立)
**用途**: 風格遷移專用
**特色**: weight_type = "style transfer"
**適合**: 保留主體但改變風格

### 4. faceid_portrait.json (待建立)
**用途**: 人臉融合
**需求**: FaceID 模型 + InsightFace
**適合**: AI 網紅、虛擬角色

## 匯入方式

1. 打開 ComfyUI: http://100.107.71.38:8188
2. 點擊 "Load" 按鈕
3. 選擇 .json 檔案
4. 載入參考圖
5. 點擊 "Queue Prompt" 生成

## 調整建議

### Weight (權重)
- 0.3-0.5: 輕微影響
- 0.6-0.8: 平衡 (推薦)
- 0.9-1.0: 強烈影響

### Denoise (去噪)
- 0.3-0.5: 保留原圖 95%
- 0.6-0.7: 80% 神韻 (推薦)
- 0.8-0.9: 大幅改變

### Steps (步數)
- 8-12: 快速測試
- 20-30: 高品質輸出
- 40+: 極致細節

## 大地起源專用參數

根據品牌需求調整:
- **產品照融合**: weight=0.7, denoise=0.65
- **自然風景**: weight=0.8, denoise=0.70
- **文字疊加用圖**: denoise=0.60 (保留構圖)

## 故障排除

### 生成結果太像參考圖
→ 降低 weight 或增加 denoise

### 生成結果偏離太多
→ 提高 weight 或降低 denoise

### 節點報錯 "Model not found"
→ 檢查模型檔案是否在 `models/ipadapter/`

### 顏色怪異
→ 嘗試不同 weight_type 或調整 CFG scale

## 下一步

1. 測試基礎工作流
2. 調整參數找到最佳設定
3. 整合到 `/Users/yuan/comfyui_tools/img2img.py`
4. 建立批次處理腳本

---

**相關文件**: `/Users/yuan/comfyui_tools/IP_ADAPTER_INSTALLATION_GUIDE.md`

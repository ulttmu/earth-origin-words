# IP-Adapter 快速上手指南

> 5 分鐘了解 IP-Adapter 並開始使用

## 什麼是 IP-Adapter?

**簡單來說**: 讓你用「圖片」控制 AI 生成，而不只是「文字」。

**核心功能**:
1. **圖+圖融合**: 混合 2-5 張圖片創造新圖
2. **風格遷移**: 讓生成圖具有參考圖的風格
3. **主體替換**: 保留構圖但替換主體內容

**類比**:
- LoRA = 訓練一個風格 (需時間和資料)
- IP-Adapter = 即時套用圖片風格 (無需訓練)

---

## 與現有 img2img 的差異

| 功能 | img2img | IP-Adapter |
|------|---------|------------|
| **輸入** | 1 張圖 | 1-5 張圖 |
| **控制方式** | denoise 參數 | weight + weight_type |
| **適用場景** | 修改單圖 | 風格融合、多圖混合 |
| **速度** | 快 | 略慢 |
| **自由度** | 低 | 高 |

**結論**: 兩者互補，可串接使用
- IP-Adapter 做風格融合 → img2img 精修細節

---

## 3 個必備模型

下載並放到對應目錄即可使用:

### 1. CLIP Vision (圖片編碼器)
```
檔案: CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
大小: 2.5 GB
位置: ComfyUI/models/clip_vision/
```

### 2. IP-Adapter SD1.5 (基礎版)
```
檔案: ip-adapter_sd15.safetensors
大小: 90 MB
位置: ComfyUI/models/ipadapter/
```

### 3. IP-Adapter Plus SD1.5 (增強版)
```
檔案: ip-adapter-plus_sd15.safetensors
大小: 90 MB
位置: ComfyUI/models/ipadapter/
```

**總下載量**: ~2.7 GB

---

## 安裝步驟 (3 步驟)

### 步驟 1: 安裝插件 (2 分鐘)
```
1. 打開 ComfyUI Manager
2. 搜尋 "ipadapter"
3. 安裝 "ComfyUI_IPAdapter_plus"
4. 重啟 ComfyUI
```

### 步驟 2: 下載模型 (15-30 分鐘)
```
下載上述 3 個模型檔案
放到對應目錄
```

### 步驟 3: 測試 (5 分鐘)
```
1. 建立新工作流
2. 加入 IPAdapter Apply 節點
3. 載入參考圖
4. 生成測試
```

---

## 基礎用法 (節點連接)

### 最簡單的工作流
```
Load Checkpoint (SD 1.5 模型)
    ↓
Load Image (參考圖)
    ↓
IPAdapter Apply
    ↓
KSampler (prompt + 生成參數)
    ↓
VAE Decode
    ↓
Save Image
```

### 雙圖融合工作流
```
Load Image A ─┐
              ├→ Batch Image
Load Image B ─┘       ↓
                 IPAdapter Apply
                       ↓
                   KSampler
                       ↓
                   生成融合圖
```

---

## 關鍵參數說明

### weight (權重)
- **0.3-0.5**: 輕微影響，保留 prompt 主導
- **0.6-0.8**: 平衡影響 (推薦)
- **0.9-1.0**: 強烈影響，接近參考圖

**建議**: 從 0.7 開始測試

### weight_type (權重類型)
- **standard**: 通用型，整體影響
- **style transfer**: 只遷移風格，保留主體
- **composition**: 保留構圖
- **strong style transfer**: 強風格遷移

**建議**: 先用 "standard"，再試 "style transfer"

### start_at / end_at (套用區間)
- **0.0 - 1.0**: 全程套用
- **0.2 - 0.8**: 中段套用 (減少過度影響)

**建議**: 預設 0.0 - 1.0

---

## 實戰範例: 大地起源社群圖

### 需求
融合產品照 + 自然風景，產生有品牌調性的社群圖

### 參數設定
```yaml
參考圖 A: 產品照 (肥皂/沐浴用品)
參考圖 B: 森林/苔蘚/自然光影
Weight: 0.75
Weight Type: standard
Denoise: 0.70
Steps: 20
Prompt: "natural skincare product, warm lighting, forest ambiance"
```

### 調整策略
- 產品太模糊? → 提高產品照 weight 或降低 denoise
- 風格不夠自然? → 提高風景照 weight
- 構圖偏離? → 嘗試 weight_type: "composition"

---

## 多圖融合 (進階)

### 使用 IPAdapter Encoder

**節點流程**:
```
Image A → IPAdapter Encoder (weight=0.4)
Image B → IPAdapter Encoder (weight=0.3)
Image C → IPAdapter Encoder (weight=0.3)
    ↓
IPAdapter Combine Embeds
    ↓
IPAdapter Apply Encoded
    ↓
KSampler
```

**Combine Methods**:
- `average`: 平均混合 (推薦)
- `concat`: 串接特徵
- `add`: 相加
- `subtract`: 相減

---

## 常見問題速解

### Q1: 生成結果太像參考圖
**解決**: 降低 weight (0.6-0.7) 或增加 denoise (0.8+)

### Q2: 生成結果偏離太多
**解決**: 提高 weight (0.8-0.9) 或降低 denoise (0.5-0.6)

### Q3: 節點找不到
**解決**: 確認已安裝插件並重啟 ComfyUI

### Q4: 模型載入失敗
**解決**: 檢查檔案名稱和路徑是否正確

### Q5: 顏色怪異
**解決**: 調整 CFG scale 或嘗試不同 weight_type

---

## 下一步建議

### 1. 測試基礎工作流
- [ ] 單圖風格遷移
- [ ] 雙圖融合
- [ ] 調整參數找最佳設定

### 2. 建立自己的預設
- [ ] 找到適合品牌的參數組合
- [ ] 儲存為工作流模板
- [ ] 建立參數查詢表

### 3. 整合到生產流程
- [ ] 修改 `img2img.py` 支援多圖
- [ ] 建立批次處理腳本
- [ ] 自動化參考圖選擇

---

## 參數速查表

### 大地起源專用設定

| 用途 | Weight | Weight Type | Denoise | Steps |
|------|--------|-------------|---------|-------|
| 產品照+風景 | 0.75 | standard | 0.70 | 20 |
| 純風格遷移 | 0.80 | style transfer | 0.65 | 25 |
| 保留構圖 | 0.70 | composition | 0.60 | 20 |
| 人物融合 | 0.85 | standard | 0.75 | 30 |

---

## 資源連結

### 詳細文件
- 完整安裝指南: `/Users/yuan/comfyui_tools/IP_ADAPTER_INSTALLATION_GUIDE.md`
- 安裝檢查清單: `/Users/yuan/comfyui_tools/IP_ADAPTER_CHECKLIST.md`
- 模型下載腳本: `/Users/yuan/comfyui_tools/download_ipadapter_models.py`

### 線上資源
- GitHub 官方: https://github.com/cubiq/ComfyUI_IPAdapter_plus
- Hugging Face 模型: https://huggingface.co/h94/IP-Adapter
- 教學影片: https://www.runcomfy.com/tutorials/comfyui-ipadapter-plus-deep-dive-tutorial

### ComfyUI 位置
- Windows PC: http://100.107.71.38:8188
- 模型目錄: `D:\ComfyUI_windows_portable\ComfyUI\models\`

---

## 總結

**IP-Adapter 的價值**:
1. 不需訓練 LoRA 即可做風格遷移
2. 支援多圖融合創造獨特風格
3. 參數調整靈活，適合實驗
4. 與 img2img、ControlNet 可串接

**適合誰**:
- 需要快速風格測試
- 想要混合多種參考圖
- 不想花時間訓練模型
- 追求創意實驗

**開始使用**:
跟著檢查清單完成安裝，5 分鐘就能生成第一張融合圖！

---

**更新日期**: 2025-12-26
**ComfyUI 版本**: 0.6.0
**作者**: Claude Code - 大地起源 AIGC 系統

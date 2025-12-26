# ComfyUI IP-Adapter 安裝指南

> 更新日期: 2025-12-26
> ComfyUI 版本: 0.6.0
> Windows PC: 100.107.71.38:8188

## 概述

IP-Adapter 是強大的圖片融合技術，可以：
- **圖+圖融合**: 混合多張圖片創造新圖
- **風格遷移**: 將參考圖的風格套用到生成圖
- **主體替換**: 保留構圖但替換主體
- **精確控制**: 每張參考圖可設定不同權重

想像它是「1-image LoRA」—— 不需要訓練模型就能做風格遷移。

---

## 安裝步驟

### 方法一: 使用 ComfyUI Manager (推薦)

1. **開啟 ComfyUI Manager**
   - 點擊 ComfyUI 右側面板的 "Manager" 按鈕
   - 點擊 "Custom Nodes Manager"

2. **搜尋並安裝**
   - 在搜尋框輸入: `ipadapter`
   - 找到 `ComfyUI_IPAdapter_plus` (作者: cubiq)
   - 點擊 "Install"
   - 安裝完成後點擊 "RESTART" 重啟 ComfyUI

### 方法二: 手動安裝

```bash
# 在 Windows PC 上執行 (透過遠端桌面或 SSH)
cd D:\ComfyUI_windows_portable\ComfyUI\custom_nodes
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
```

---

## 下載模型檔案

### 1. CLIP Vision 模型 (必需)

下載以下兩個檔案並放到 `ComfyUI/models/clip_vision/`:

| 檔案名稱 | 下載連結 | 大小 |
|---------|---------|------|
| `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` | [Hugging Face](https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors) | ~2.5 GB |
| `CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors` | [Hugging Face](https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/image_encoder/model.safetensors) | ~3.7 GB |

**放置位置**: `D:\ComfyUI_windows_portable\ComfyUI\models\clip_vision\`

### 2. IP-Adapter 模型 (基礎)

下載並放到 `ComfyUI/models/ipadapter/`:

#### SD 1.5 模型
| 檔案名稱 | 用途 | 下載連結 |
|---------|------|---------|
| `ip-adapter_sd15.safetensors` | 基礎版 | [Hugging Face](https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter_sd15.safetensors) |
| `ip-adapter-plus_sd15.safetensors` | 增強版 | [Hugging Face](https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.safetensors) |
| `ip-adapter-plus-face_sd15.safetensors` | 人臉專用 | [Hugging Face](https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus-face_sd15.safetensors) |

#### SDXL 模型
| 檔案名稱 | 用途 | 下載連結 |
|---------|------|---------|
| `ip-adapter_sdxl_vit-h.safetensors` | SDXL 基礎 | [Hugging Face](https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl_vit-h.safetensors) |
| `ip-adapter-plus_sdxl_vit-h.safetensors` | SDXL 增強 | [Hugging Face](https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors) |

**放置位置**: `D:\ComfyUI_windows_portable\ComfyUI\models\ipadapter\`

### 3. FaceID 模型 (選用)

如需人臉融合功能，下載以下檔案：

| 檔案名稱 | 下載連結 |
|---------|---------|
| `ip-adapter-faceid_sd15.bin` | [Hugging Face](https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sd15.bin) |
| `ip-adapter-faceid-plusv2_sd15.bin` | [Hugging Face](https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sd15.bin) |
| `ip-adapter-faceid_sdxl.bin` | [Hugging Face](https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sdxl.bin) |

**額外需求**: FaceID 需要安裝 InsightFace

```bash
# 在 Windows PC 的 ComfyUI 目錄執行
# 先下載對應 Python 版本的 .whl 檔案 (你的 Python 是 3.10.9)
.\python_embeded\python.exe -m pip install insightface-0.7.3-cp310-cp310-win_amd64.whl
```

---

## 目錄結構檢查

安裝完成後，目錄應該如下：

```
D:\ComfyUI_windows_portable\ComfyUI\
├── custom_nodes/
│   └── ComfyUI_IPAdapter_plus/
│       ├── __init__.py
│       ├── IPAdapterPlus.py
│       └── ...
├── models/
│   ├── clip_vision/
│   │   ├── CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
│   │   └── CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors
│   └── ipadapter/
│       ├── ip-adapter_sd15.safetensors
│       ├── ip-adapter-plus_sd15.safetensors
│       ├── ip-adapter_sdxl_vit-h.safetensors
│       └── ...
```

---

## 基本使用方法

### 工作流 1: 雙圖融合 (最簡單)

```
節點連接:
1. Load Image (圖片 A)
2. Load Image (圖片 B)
3. Batch Image → 合併 A 和 B
4. IPAdapter Apply → 套用到 KSampler
5. KSampler → 生成融合圖
```

**關鍵參數**:
- `weight`: 0.5-1.0 (0.8 推薦)
- `weight_type`: "standard" 或 "style transfer"
- `start_at`: 0.0 (從頭套用)
- `end_at`: 1.0 (套用到尾)

### 工作流 2: 多圖融合 (進階)

使用 `IPAdapter Encoder` + `IPAdapter Combine Embeds`:

```
節點連接:
1. Load Image A → IPAdapter Encoder (weight=0.4)
2. Load Image B → IPAdapter Encoder (weight=0.3)
3. Load Image C → IPAdapter Encoder (weight=0.3)
4. IPAdapter Combine Embeds → 合併所有 Embeds
   - combine_method: "average" (平均) 或 "concat" (串接)
5. IPAdapter Apply Encoded → 套用到 KSampler
```

**Combine Methods**:
- `concat`: 串接所有圖片特徵
- `add`: 相加
- `subtract`: 相減
- `average`: 平均值
- `norm average`: 標準化平均

### 工作流 3: 風格遷移

```
節點設定:
1. IPAdapter Advanced
   - weight_type: "style transfer (SDXL)"
   - weight: 0.7-1.0
2. (選用) 搭配 ControlNet Lineart 保留主體輪廓
```

---

## 參數調整建議

### Weight (權重)
- `0.3-0.5`: 輕微影響，保留原始 prompt
- `0.6-0.8`: 平衡影響 (推薦)
- `0.9-1.0`: 強烈影響，接近參考圖

### Weight Type
- `standard`: 通用型，影響整體
- `style transfer`: 只遷移風格，保留主體
- `composition`: 保留構圖
- `strong style transfer`: 強風格遷移

### Start/End At
- `start_at=0.0, end_at=1.0`: 全程套用
- `start_at=0.2, end_at=0.8`: 中段套用 (避免過度影響)

---

## 常見問題排解

### 1. 安裝後找不到節點
**解決方法**:
- 確認 ComfyUI 已重啟
- 檢查 `custom_nodes/ComfyUI_IPAdapter_plus/` 目錄存在
- 查看 ComfyUI 終端機是否有錯誤訊息

### 2. 模型載入失敗
**可能原因**:
- 檔案名稱不正確 (需完全符合)
- 檔案放錯目錄
- 檔案下載不完整 (重新下載)

### 3. FaceID 節點報錯
**解決方法**:
- 確認已安裝 InsightFace
- 檢查 Python 版本 (需 3.10 或 3.11)
- 下載對應的 LoRA 檔案 (FaceID Plus V2 需要)

### 4. 生成結果不理想
**調整建議**:
- 降低 weight 到 0.7-0.8
- 增加 sampling steps (20-30)
- 嘗試不同 weight_type
- 確認參考圖解析度足夠 (建議 512x512 以上)

---

## 實用範例

### 範例 1: 大地起源產品照 + 自然風景
```
目標: 將產品照融合自然背景

參考圖 A: 產品照 (weight=0.6)
參考圖 B: 森林風景 (weight=0.4)
Prompt: "natural skincare product on moss, soft lighting"
IPAdapter: standard, weight=0.8
```

### 範例 2: 多風格混合
```
參考圖 A: 溫暖色調 (weight=0.3)
參考圖 B: 極簡構圖 (weight=0.4)
參考圖 C: 自然光影 (weight=0.3)
Method: average
```

---

## 與現有 img2img 比較

| 功能 | img2img | IP-Adapter |
|------|---------|------------|
| 主要用途 | 修改單張圖 | 融合多張圖 |
| 控制精度 | denoise 參數 | weight + weight_type |
| 多圖支援 | 無 | 原生支援 |
| 風格遷移 | 需高 denoise | 專用 weight_type |
| 速度 | 快 | 略慢 (需編碼) |

**建議整合**:
- 圖片修改用 img2img (denoise 控制)
- 多圖融合用 IP-Adapter
- 可串接使用: IP-Adapter 生成 → img2img 精修

---

## 快速測試

安裝完成後，執行以下測試：

### 測試 1: 檢查節點可用性
1. 重啟 ComfyUI
2. 右鍵空白處 → Add Node → ipadapter
3. 確認出現: IPAdapter Apply, IPAdapter Encoder 等節點

### 測試 2: 基礎生成
1. 使用現有 img2img 工作流
2. 插入 `IPAdapter Apply` 節點
3. 載入一張參考圖
4. 生成測試 (weight=0.8)

---

## 進階資源

### 官方範例
GitHub repo 的 `examples/` 目錄有完整工作流:
- Basic usage
- Multi-image fusion
- FaceID workflows
- Style transfer

### 社群工作流
- [Civitai - Combine Multiple Images](https://civitai.com/articles/3099/combine-multiple-images-with-ipadapter-a-workflow-for-comfyui)
- [RunComfy - IPAdapter Plus Tutorial](https://www.runcomfy.com/tutorials/comfyui-ipadapter-plus-deep-dive-tutorial)

### 模型庫
- [Hugging Face - h94/IP-Adapter](https://huggingface.co/h94/IP-Adapter)
- [Hugging Face - LichAcademy/ipadapter-comfyui](https://huggingface.co/LichAcademy/ipadapter-comfyui)

---

## 版本注意事項

**IP-Adapter V2 重大變更**:
- 2025年4月發布的 V2 版本重寫了底層代碼
- 舊的 V1 工作流不相容 V2
- 如果現有工作流使用 V1，可選擇不升級
- 如需升級，必須重建所有工作流

**維護狀態** (截至 2025-12-26):
- 官方 repo 進入 "maintenance only" 模式
- 開發者不再積極更新
- 關鍵 bug 修復會持續
- 社群 fork 版本可能更活躍

---

## 下一步

1. **安裝插件**: 使用 ComfyUI Manager 安裝
2. **下載模型**: 至少下載 CLIP Vision + ip-adapter_sd15
3. **匯入範例工作流**: 從 GitHub 下載 examples
4. **整合到現有系統**: 修改 `/Users/yuan/comfyui_tools/img2img.py` 支援多圖融合

---

## 相關檔案

- ComfyUI 主程式: `D:\ComfyUI_windows_portable\ComfyUI\`
- 本地工具腳本: `/Users/yuan/comfyui_tools/`
- 參考圖庫: `~/Library/CloudStorage/GoogleDrive-.../earth-origin-iTi-ref/_processed/`

---

**作者**: Claude Code
**系統**: 大地起源 AIGC 內容生成系統
**最後更新**: 2025-12-26

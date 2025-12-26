# IP-Adapter 安裝檢查清單

> 按照此清單逐步完成 IP-Adapter 安裝

## 前置確認

- [ ] Windows PC 在線: `ping 100.107.71.38`
- [ ] ComfyUI 運行中: `curl http://100.107.71.38:8188/system_stats`
- [ ] 有足夠硬碟空間 (至少 15 GB 可用)
- [ ] 確認 Python 版本 (3.10.9 ✓)

---

## 步驟 1: 安裝插件

### 方法 A: ComfyUI Manager (推薦)
- [ ] 打開 http://100.107.71.38:8188
- [ ] 點擊右側 "Manager" 按鈕
- [ ] 點擊 "Custom Nodes Manager"
- [ ] 搜尋 "ipadapter"
- [ ] 找到 "ComfyUI_IPAdapter_plus" (作者: cubiq)
- [ ] 點擊 "Install"
- [ ] 點擊 "RESTART" 重啟 ComfyUI

### 方法 B: 手動安裝
- [ ] 連線到 Windows PC (遠端桌面或 SSH)
- [ ] 執行:
  ```bash
  cd D:\ComfyUI_windows_portable\ComfyUI\custom_nodes
  git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
  ```
- [ ] 重啟 ComfyUI

---

## 步驟 2: 下載 CLIP Vision 模型 (必需)

目錄: `D:\ComfyUI_windows_portable\ComfyUI\models\clip_vision\`

### 檔案 1: CLIP-ViT-H-14
- [ ] 下載: [CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors](https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors)
- [ ] 大小: ~2.5 GB
- [ ] 重新命名為: `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors`
- [ ] 放置到 `clip_vision/` 目錄

### 檔案 2: CLIP-ViT-bigG-14
- [ ] 下載: [CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors](https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/image_encoder/model.safetensors)
- [ ] 大小: ~3.7 GB
- [ ] 重新命名為: `CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors`
- [ ] 放置到 `clip_vision/` 目錄

---

## 步驟 3: 下載 IP-Adapter 基礎模型 (必需)

目錄: `D:\ComfyUI_windows_portable\ComfyUI\models\ipadapter\`

### SD 1.5 模型 (推薦先下載這兩個)
- [ ] [ip-adapter_sd15.safetensors](https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter_sd15.safetensors) (~90 MB)
- [ ] [ip-adapter-plus_sd15.safetensors](https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.safetensors) (~90 MB)

### SDXL 模型 (選用)
- [ ] [ip-adapter_sdxl_vit-h.safetensors](https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl_vit-h.safetensors) (~700 MB)
- [ ] [ip-adapter-plus_sdxl_vit-h.safetensors](https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors) (~700 MB)

---

## 步驟 4: 下載 FaceID 模型 (選用)

**如不需人臉融合功能，可跳過此步驟**

### FaceID 模型檔案
- [ ] [ip-adapter-faceid_sd15.bin](https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sd15.bin)
- [ ] [ip-adapter-faceid-plusv2_sd15.bin](https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sd15.bin)
- [ ] [ip-adapter-faceid_sdxl.bin](https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sdxl.bin)

### 安裝 InsightFace (FaceID 必需)
- [ ] 下載 InsightFace wheel: `insightface-0.7.3-cp310-cp310-win_amd64.whl`
- [ ] 在 Windows PC 執行:
  ```bash
  cd D:\ComfyUI_windows_portable
  .\python_embeded\python.exe -m pip install insightface-0.7.3-cp310-cp310-win_amd64.whl
  ```

---

## 步驟 5: 驗證安裝

### 檢查目錄結構
```
D:\ComfyUI_windows_portable\ComfyUI\
├── custom_nodes/
│   └── ComfyUI_IPAdapter_plus/  [✓]
├── models/
│   ├── clip_vision/
│   │   ├── CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors  [✓]
│   │   └── CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors  [✓]
│   └── ipadapter/
│       ├── ip-adapter_sd15.safetensors  [✓]
│       └── ip-adapter-plus_sd15.safetensors  [✓]
```

### 檢查 ComfyUI 節點
- [ ] 重啟 ComfyUI
- [ ] 打開 http://100.107.71.38:8188
- [ ] 右鍵空白處 → Add Node → 搜尋 "ipadapter"
- [ ] 確認出現以下節點:
  - [ ] IPAdapter Apply
  - [ ] IPAdapter Advanced
  - [ ] IPAdapter Encoder
  - [ ] IPAdapter Combine Embeds
  - [ ] IPAdapter Load Model

---

## 步驟 6: 基礎測試

### 測試 1: 單圖風格遷移
- [ ] 建立新工作流
- [ ] 加入節點:
  - Load Checkpoint (SD 1.5 模型)
  - Load Image (參考圖)
  - IPAdapter Apply
  - KSampler
  - VAE Decode
  - Save Image
- [ ] 連接節點
- [ ] 設定參數:
  - weight: 0.8
  - weight_type: standard
- [ ] 點擊 "Queue Prompt"
- [ ] 確認可以正常生成

### 測試 2: 雙圖融合
- [ ] 使用 Batch Image 合併兩張圖
- [ ] 連接到 IPAdapter Apply
- [ ] 生成測試
- [ ] 確認融合效果

---

## 步驟 7: 整合到現有工具

### 修改 img2img.py
- [ ] 備份現有 `/Users/yuan/comfyui_tools/img2img.py`
- [ ] 加入多圖融合選項
- [ ] 支援 weight 參數調整
- [ ] 測試端到端流程

### 建立快捷腳本
- [ ] 建立 `ipadapter_fusion.py` (雙圖融合)
- [ ] 建立 `ipadapter_batch.py` (批次處理)
- [ ] 整合到主工作流

---

## 常見問題檢查

### 如果節點找不到
- [ ] 確認 ComfyUI 已重啟
- [ ] 檢查 `custom_nodes/ComfyUI_IPAdapter_plus/` 存在
- [ ] 查看 ComfyUI 終端機錯誤訊息
- [ ] 嘗試手動重新安裝插件

### 如果模型載入失敗
- [ ] 確認檔案名稱完全正確 (大小寫、副檔名)
- [ ] 確認檔案大小正確 (未下載不完整)
- [ ] 檢查檔案路徑
- [ ] 重新下載模型

### 如果生成結果怪異
- [ ] 調低 weight (0.6-0.8)
- [ ] 增加 steps (20-30)
- [ ] 嘗試不同 weight_type
- [ ] 確認參考圖解析度 (建議 512x512+)

---

## 下載連結速查

### CLIP Vision
- https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors
- https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/image_encoder/model.safetensors

### IP-Adapter (SD 1.5)
- https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter_sd15.safetensors
- https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.safetensors

### IP-Adapter (SDXL)
- https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl_vit-h.safetensors
- https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors

### FaceID
- https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sd15.bin
- https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sd15.bin

---

## 完成標記

- [ ] 所有必需模型已下載
- [ ] ComfyUI 節點正常運作
- [ ] 基礎測試成功
- [ ] 已建立範例工作流
- [ ] 整合到現有工具腳本

**預計完成時間**: 1-2 小時 (依網速)

---

**相關文件**:
- 詳細安裝指南: `/Users/yuan/comfyui_tools/IP_ADAPTER_INSTALLATION_GUIDE.md`
- 下載腳本: `/Users/yuan/comfyui_tools/download_ipadapter_models.py`
- 工作流範例: `/Users/yuan/comfyui_tools/ipadapter_workflows/`

**最後更新**: 2025-12-26

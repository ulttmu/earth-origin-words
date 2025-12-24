# ComfyUI 遠端控制工具

## 架構

```
Mac Mini (本機)          Windows PC (遠端)
     │                        │
     │     Tailscale VPN      │
     ├────────────────────────┤
     │                        │
  Python 腳本  ──HTTP API──▶  ComfyUI
     │                        RTX 4070Ti Super
     ▼                        16GB VRAM
  Google Drive
  (自動同步)
```

## 連線資訊

- **Windows PC Tailscale IP**: `100.107.71.38`
- **ComfyUI URL**: `http://100.107.71.38:8188`
- **Google Drive 輸出資料夾**: `我的雲端硬碟/ComfyUI_Output/`

## 已安裝的模型

| 模型 | 類型 | 用途 |
|-----|------|------|
| z_image_turbo_bf16.safetensors | UNET | Z-Image 主模型 |
| qwen_3_4b.safetensors | Text Encoder | 文字編碼器 |
| ae.safetensors | VAE | 圖片解碼 |
| flux1-dev.safetensors | UNET | FLUX 模型 |
| clip_l.safetensors | CLIP | FLUX 用 |
| t5xxl_fp16.safetensors | Text Encoder | FLUX T5 |

## 已安裝的節點

- Z-Image Utilities
- Qwen Edit Utils
- Nano Banana Pro (需 Google API Key)
- IPAdapter Plus
- ControlNet Aux
- ComfyUI Manager
- 550+ 專業節點

## 檔案說明

| 檔案 | 說明 |
|-----|------|
| `comfyui_client.py` | ComfyUI API 客戶端基礎模組 |
| `generate_image.py` | 圖片生成腳本（自動上傳 Google Drive） |

## 使用方式

### 基本生圖

```python
from generate_image import generate_image

# 生成圖片（自動上傳到 Google Drive）
result = generate_image(
    prompt="a beautiful product photo of handmade soap, white background",
    width=1024,
    height=1024,
    steps=8
)
print(f"圖片已儲存: {result}")
```

### 測試連線

```bash
python comfyui_client.py
```

## 效能

- **生成速度**: ~14-18 秒 / 張 (1024x1024, 8 steps)
- **GPU**: RTX 4070Ti Super
- **VRAM**: 16GB

## 待完成功能

- [ ] 批次處理腳本
- [ ] img2img 編輯功能
- [ ] Gradio 網頁介面
- [ ] 中文提示詞優化

## 建立日期

2025-12-25

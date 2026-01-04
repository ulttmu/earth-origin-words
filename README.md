# Earth Origin - ComfyUI 圖片生成工具

大地起源品牌 Meta 廣告配圖自動化生成系統

## 功能特色

- 🎨 **批次圖片生成** - 為 Airtable 廣告文案批次生成配圖
- 🖼️ **智能視覺設計** - 根據產品自動設計 3 個視覺方向
- 🤖 **ComfyUI 整合** - 使用 Z-Image Turbo 快速生成高品質圖片
- ☁️ **Google Drive 同步** - 自動上傳並獲取公開分享連結
- 📊 **Airtable 整合** - 直接在 Airtable 預覽生成的圖片

## 環境變數設定

複製 `.env.example` 為 `.env` 並填入你的 API tokens：

```bash
cp .env.example .env
```

## 使用方式

```bash
# 設定環境變數
export AIRTABLE_API_TOKEN=your_token_here

# 執行批次生成
python batch_airtable_images.py
```

## 授權

Private - 大地起源品牌專用

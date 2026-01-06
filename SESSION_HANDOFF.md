# ComfyUI 產品合成項目 - 工作交接文檔

**日期**: 2026-01-06
**當前狀態**: Z-Image Edit Workflow 已創建，等待測試
**Windows PC**: 100.107.71.38 (Tailscale)
**SSH 連接**: `ssh user@100.107.71.38`

---

## 📊 當前進度總覽

### ✅ 已完成

1. **SSH 遠端連接設置**
   - Mac 可以免密碼 SSH 到 Windows PC
   - 命令：`ssh user@100.107.71.38`
   - 公鑰已配置在兩個位置（管理員用戶）

2. **IOPaint 安裝**
   - 版本：1.6.0
   - Web UI：http://100.107.71.38:8080
   - 功能：圖片修復、物體移除
   - 桌面啟動腳本：`Start_IOPaint.bat`, `IOPaint_Batch.bat`

3. **ComfyUI 環境確認**
   - 路徑：`C:\ComfyUI`
   - 模型：FLUX-dev (22GB), Z-Image Turbo (11GB)
   - Custom Nodes：完整安裝（包括 Z-Image, IP-Adapter, Inpainting, 去背等）
   - ControlNet：Canny & Depth 已就緒
   - Web UI：http://100.107.71.38:8188

4. **Z-Image Edit Workflow 創建**
   - 文件：`C:\Users\user\Desktop\product_placement_workflow.json`
   - 用途：產品圖 + 場景圖 → 自然合成
   - 功能：塗改指定位置、參考產品外觀、自動光影匹配

5. **文檔創建**
   - 使用指南：`/Users/yuan/comfyui_tools/zimage_setup_guide.md`
   - CLAUDE.md 已更新（SSH + IOPaint 資訊）

### ⏸️ 進行中

1. **載入和測試 Z-Image Workflow**
   - Workflow 已上傳到 Windows PC 桌面
   - ComfyUI 已啟動（http://100.107.71.38:8188）
   - 等待：載入 workflow 並測試產品合成

### 📋 待辦事項

1. **載入 Workflow**
   - 拖放 `product_placement_workflow.json` 到 ComfyUI
   - 檢查是否有節點錯誤
   - 如有錯誤，修正節點名稱

2. **準備測試圖片**
   - 產品圖：大地起源洗髮精瓶（已提供）
   - 場景圖：侘寂風木架（已提供）
   - 需要複製到：`C:\ComfyUI\input\`

3. **執行首次測試**
   - 載入場景圖
   - 載入產品圖
   - 塗改想放產品的位置（mask）
   - 調整參數並執行

4. **優化和調整**
   - 根據首次結果調整參數
   - 優化 prompt
   - 可能需要調整 strength/reference_strength

5. **批次處理設置**（可選）
   - 如果效果滿意，創建批次處理腳本
   - 自動處理多張產品圖

---

## 🔧 技術細節

### Z-Image Edit Workflow 架構

```
產品圖（參考）
    ↓
場景圖 → 塗 Mask → Z-Image Edit → 合成結果
              ↓
         (指定位置)
```

### 關鍵參數

| 參數 | 推薦值 | 說明 |
|------|--------|------|
| Strength | 0.8 | 保留場景程度（0.7-0.9） |
| Reference Strength | 0.85 | 參考產品圖程度（0.8-0.95） |
| Guidance Scale | 7.0 | 遵循 prompt 程度（5-10） |
| Steps | 20 | 生成品質（15-30） |

### Prompt 範例

```
place earth origin shampoo bottle naturally on rustic wooden shelf,
warm ambient lighting, wabi-sabi aesthetic,
natural shadows, integrate seamlessly with ceramic jars and natural items
```

---

## 🚀 繼續工作的步驟

### 立即行動

1. **確認 ComfyUI 運行**
   ```bash
   curl http://100.107.71.38:8188
   ```
   如果沒有回應：
   ```bash
   ssh user@100.107.71.38 'powershell -Command "cd C:\ComfyUI; python main.py --listen 0.0.0.0 --port 8188"'
   ```

2. **打開 ComfyUI**
   - 瀏覽器：http://100.107.71.38:8188

3. **載入 Workflow**
   - 方式 1：拖放桌面的 `product_placement_workflow.json`
   - 方式 2：點擊 Load 按鈕選擇文件

4. **如果遇到節點錯誤**
   - 截圖錯誤訊息
   - 在 ComfyUI 中搜尋 "zimage" 或 "z-image" 查看實際節點名稱
   - 修正 workflow 中的節點類型

### 準備圖片

使用者的圖片需要：
- 產品圖：洗髮精瓶（棕色玻璃瓶，白色標籤）
- 場景圖：侘寂風木架（陶器、織物、自然元素）

透過 SSH 複製到 ComfyUI：
```bash
# 假設圖片在某個位置
scp product.png user@100.107.71.38:'C:\ComfyUI\input\product.png'
scp scene.png user@100.107.71.38:'C:\ComfyUI\input\scene.png'
```

---

## 🐛 已知問題和解決方案

### 1. ComfyUI 節點名稱不確定

**問題**：Workflow 中的 `ZImageEdit_Turbo` 可能不是正確的節點名稱

**解決**：
1. 在 ComfyUI 中右鍵 → Add Node → 搜尋 "zimage"
2. 查看實際的節點名稱
3. 修改 workflow JSON 中的節點類型

### 2. 模型路徑問題

**確認模型位置**：
```bash
ssh user@100.107.71.38 'powershell -Command "Get-ChildItem C:\ComfyUI\models\diffusion_models\z_image*.safetensors"'
```

應該看到：`z_image_turbo_bf16.safetensors`

### 3. 如果 Z-Image 不可用

**備選方案**：
- 使用 Qwen Image Edit 模板（ComfyUI 內建）
- 或請 PC 端 Claude 安裝 IC-Light 模型

---

## 📂 重要文件位置

### Mac 端
| 文件 | 路徑 |
|------|------|
| Workflow JSON | `/Users/yuan/comfyui_tools/product_placement_workflow.json` |
| 使用指南 | `/Users/yuan/comfyui_tools/zimage_setup_guide.md` |
| SSH 設置指南 | `/Users/yuan/comfyui_tools/setup_ssh_key.md` |
| 診斷腳本 | `/Users/yuan/comfyui_tools/diagnose_ssh.md` |
| CLAUDE.md | `/Users/yuan/CLAUDE.md` |

### Windows PC
| 文件 | 路徑 |
|------|------|
| ComfyUI | `C:\ComfyUI` |
| Workflow | `C:\Users\user\Desktop\product_placement_workflow.json` |
| Input 圖片 | `C:\ComfyUI\input\` |
| Output 結果 | `C:\ComfyUI\output\` |
| IOPaint 腳本 | `C:\Users\user\Desktop\Start_IOPaint.bat` |

---

## 💡 給新 Claude 的提示

### 如果 Workflow 載入失敗

1. **檢查實際節點名稱**
   ```python
   # 在 Windows PC 上執行
   import sys
   sys.path.append('C:/ComfyUI')
   import nodes

   # 搜尋 Z-Image 相關節點
   for name in nodes.NODE_CLASS_MAPPINGS.keys():
       if 'zimage' in name.lower() or 'z-image' in name.lower() or 'z_image' in name.lower():
           print(f"Found: {name}")
   ```

2. **修改 Workflow JSON**
   - 找到正確的節點類型名稱
   - 編輯 workflow JSON
   - 替換節點的 "type" 欄位

3. **使用內建模板**
   - 如果 Z-Image 設置複雜，直接使用 ComfyUI 的 Qwen Image Edit 模板
   - 或 Flux 2 Inpainting 模板

### 測試策略

1. **先低參數快速測試**
   - Steps: 15
   - Size: 512x512
   - 確認 workflow 可以運行

2. **調整 Prompt 和位置**
   - 找到最佳的產品放置位置
   - 優化 prompt 描述

3. **提高品質**
   - Steps: 25
   - Size: 768x768 或更大
   - 精細調整參數

---

## 🔗 快速連接

- **ComfyUI**: http://100.107.71.38:8188
- **IOPaint**: http://100.107.71.38:8080
- **SSH**: `ssh user@100.107.71.38`
- **Tailscale Status**: `tailscale status`

---

## 📞 如果遇到問題

### ComfyUI 無法訪問
```bash
ssh user@100.107.71.38 'powershell -Command "Get-Process python; netstat -ano | Select-String :8188"'
```

### 重啟 ComfyUI
```bash
ssh user@100.107.71.38 'powershell -Command "Get-Process python | Stop-Process -Force; cd C:\ComfyUI; Start-Process powershell -ArgumentList \"-NoExit\", \"-Command\", \"python main.py --listen 0.0.0.0 --port 8188\" -WindowStyle Minimized"'
```

### 檢查模型
```bash
ssh user@100.107.71.38 'powershell -Command "Get-ChildItem C:\ComfyUI\models\diffusion_models"'
```

---

## ✅ 成功標準

當完成以下所有項目時，項目階段一完成：

- [ ] Workflow 成功載入到 ComfyUI
- [ ] 可以載入產品圖和場景圖
- [ ] 可以塗改遮罩指定位置
- [ ] 成功生成至少一張合成圖
- [ ] 合成效果自然（光影匹配、位置合理）
- [ ] 使用者滿意結果

---

**下一個 Claude，加油！** 🚀

有任何問題可以參考：
- `/Users/yuan/CLAUDE.md` - 完整系統文檔
- `/Users/yuan/comfyui_tools/zimage_setup_guide.md` - 詳細使用指南

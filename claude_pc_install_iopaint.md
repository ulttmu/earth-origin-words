# IOPaint 安裝指令 - 給 Windows PC Claude

請幫我在這台 Windows PC 上安裝並啟動 IOPaint (https://github.com/Sanster/IOPaint)。

## 系統資訊
- GPU: RTX 4070 Ti Super (16GB VRAM)
- Python: 3.10.9
- PyTorch: 2.3.1+cu121
- ComfyUI 已運行在: http://localhost:8188

## 安裝要求

1. **安裝 IOPaint**
   ```powershell
   pip install iopaint --upgrade
   ```

2. **創建啟動腳本** - 存到桌面 `Start_IOPaint.bat`
   ```batch
   @echo off
   title IOPaint Server
   echo ========================================
   echo IOPaint Server - Starting...
   echo ========================================
   echo.
   echo Web UI will be available at:
   echo   http://localhost:8080
   echo   http://100.107.71.38:8080 (Tailscale LAN)
   echo.
   echo Press Ctrl+C to stop
   echo ========================================
   echo.

   iopaint start --model=lama --device=cuda --port=8080 --host=0.0.0.0

   pause
   ```

3. **創建批次處理腳本** - 存到桌面 `IOPaint_Batch.bat`
   ```batch
   @echo off
   title IOPaint Batch Processing
   echo ========================================
   echo IOPaint 批次處理
   echo ========================================
   echo.

   set /p INPUT_FOLDER="請輸入輸入資料夾路徑: "
   set /p OUTPUT_FOLDER="請輸入輸出資料夾路徑: "

   if not exist "%OUTPUT_FOLDER%" mkdir "%OUTPUT_FOLDER%"

   echo.
   echo 開始批次處理...
   echo 輸入: %INPUT_FOLDER%
   echo 輸出: %OUTPUT_FOLDER%
   echo.

   iopaint run --model=lama --device=cuda --image="%INPUT_FOLDER%\*.jpg" --output="%OUTPUT_FOLDER%"

   echo.
   echo 處理完成！
   pause
   ```

4. **測試安裝**
   ```powershell
   iopaint --version
   ```

5. **立即啟動（測試用）**
   ```powershell
   iopaint start --model=lama --device=cuda --port=8080 --host=0.0.0.0
   ```

## 預期結果

安裝完成後應該會：
- ✅ pip 成功安裝 iopaint
- ✅ 桌面出現 `Start_IOPaint.bat` 和 `IOPaint_Batch.bat`
- ✅ 執行 `iopaint --version` 顯示版本號
- ✅ 啟動後可以訪問 http://localhost:8080
- ✅ 從 Mac 可以訪問 http://100.107.71.38:8080

## 安裝後請回報

完成後請告訴我：
1. IOPaint 版本號
2. Web UI 是否可以訪問
3. 是否有任何錯誤訊息

## 備註

- IOPaint 會在首次啟動時自動下載 lama 模型（約 200MB）
- 使用 GPU 加速，適合批次處理大量產品圖
- 支援圖片修復、物體移除、背景替換等功能

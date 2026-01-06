# IOPaint 安裝腳本 - Windows PC
# 執行方式：以管理員權限開啟 PowerShell，然後執行此腳本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "IOPaint 安裝腳本 - 大地起源 AIGC 系統" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 Python 版本
Write-Host "1. 檢查 Python 版本..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Python 未安裝或不在 PATH 中" -ForegroundColor Red
    exit 1
}

# 檢查 pip
Write-Host "2. 檢查 pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "   ✓ pip 已安裝" -ForegroundColor Green
} catch {
    Write-Host "   ✗ pip 未安裝" -ForegroundColor Red
    exit 1
}

# 檢查 CUDA
Write-Host "3. 檢查 CUDA..." -ForegroundColor Yellow
try {
    $cudaVersion = nvidia-smi 2>&1 | Select-String "CUDA Version"
    Write-Host "   ✓ CUDA 可用" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ CUDA 不可用，將使用 CPU 模式" -ForegroundColor Yellow
}

# 安裝 IOPaint
Write-Host ""
Write-Host "4. 安裝 IOPaint..." -ForegroundColor Yellow
Write-Host "   這可能需要幾分鐘..." -ForegroundColor Gray

try {
    pip install iopaint --upgrade 2>&1 | Out-Null
    Write-Host "   ✓ IOPaint 安裝成功" -ForegroundColor Green
} catch {
    Write-Host "   ✗ 安裝失敗" -ForegroundColor Red
    Write-Host "   錯誤訊息: $_" -ForegroundColor Red
    exit 1
}

# 創建啟動腳本
Write-Host ""
Write-Host "5. 創建啟動腳本..." -ForegroundColor Yellow

$startupScript = @"
@echo off
title IOPaint Server
echo ========================================
echo IOPaint Server - Starting...
echo ========================================
echo.
echo Web UI will be available at:
echo   http://localhost:8080
echo   http://100.107.71.38:8080 (LAN)
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

iopaint start --model=lama --device=cuda --port=8080 --host=0.0.0.0

pause
"@

$scriptPath = "$env:USERPROFILE\Desktop\Start_IOPaint.bat"
$startupScript | Out-File -FilePath $scriptPath -Encoding ASCII

Write-Host "   ✓ 啟動腳本已創建: $scriptPath" -ForegroundColor Green

# 創建批次處理腳本
$batchScript = @"
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
"@

$batchScriptPath = "$env:USERPROFILE\Desktop\IOPaint_Batch.bat"
$batchScript | Out-File -FilePath $batchScriptPath -Encoding ASCII

Write-Host "   ✓ 批次處理腳本已創建: $batchScriptPath" -ForegroundColor Green

# 測試安裝
Write-Host ""
Write-Host "6. 測試安裝..." -ForegroundColor Yellow
try {
    $iopaintVersion = iopaint --version 2>&1
    Write-Host "   ✓ IOPaint 版本: $iopaintVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ IOPaint 未正確安裝" -ForegroundColor Red
    exit 1
}

# 完成
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安裝完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "1. 雙擊桌面上的 'Start_IOPaint.bat' 啟動服務" -ForegroundColor White
Write-Host "2. 開啟瀏覽器訪問: http://localhost:8080" -ForegroundColor White
Write-Host "3. 使用 'IOPaint_Batch.bat' 進行批次處理" -ForegroundColor White
Write-Host ""
Write-Host "支援的模型：" -ForegroundColor Yellow
Write-Host "  - lama (推薦): 通用圖片修復" -ForegroundColor White
Write-Host "  - ldm: 大型物體移除" -ForegroundColor White
Write-Host "  - mat: 遮罩修復" -ForegroundColor White
Write-Host "  - fcf: 快速修復" -ForegroundColor White
Write-Host ""
Write-Host "按任意鍵退出..." -ForegroundColor Gray
pause

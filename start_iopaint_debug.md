# 診斷並啟動 IOPaint - 給 Windows PC Claude

Mac 端無法連接到 http://100.107.71.38:8080，需要診斷並正確啟動 IOPaint。

## 診斷步驟

### 1. 檢查 IOPaint 是否正在運行

```powershell
# 檢查 IOPaint 進程
Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime

# 檢查端口 8080 是否被佔用
netstat -ano | Select-String ":8080"

# 如果有進程，停止它們
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

### 2. 測試 IOPaint 安裝

```powershell
# 檢查 IOPaint 是否正確安裝
pip show iopaint

# 測試 IOPaint 命令
iopaint --help
```

### 3. 啟動 IOPaint（前台，查看錯誤）

```powershell
# 在當前窗口啟動 IOPaint，查看詳細輸出
iopaint start --model=lama --device=cuda --port=8080 --host=0.0.0.0
```

**預期輸出**:
- 首次啟動會下載 lama 模型（約 200MB，需要幾分鐘）
- 顯示 "Running on http://0.0.0.0:8080"
- 不應該有錯誤訊息

**常見錯誤**:
1. **模型下載失敗**: 網路問題，重新執行
2. **CUDA 錯誤**: 檢查 GPU 是否被其他程序佔用
3. **端口被佔用**: 更換端口或關閉佔用程序

### 4. 如果前台啟動成功，在背景啟動

```powershell
# 停止前台進程（Ctrl+C）

# 在背景啟動
Start-Process powershell -ArgumentList "-NoExit", "-Command", "iopaint start --model=lama --device=cuda --port=8080 --host=0.0.0.0" -WindowStyle Minimized

# 等待幾秒
Start-Sleep -Seconds 10

# 確認服務運行
netstat -ano | Select-String ":8080.*LISTENING"

# 測試本地訪問
Invoke-WebRequest -Uri "http://localhost:8080" -UseBasicParsing | Select-Object StatusCode
```

### 5. 檢查防火牆

```powershell
# 檢查防火牆規則
Get-NetFirewallRule -DisplayName "*IOPaint*" -ErrorAction SilentlyContinue

# 如果沒有規則，創建一個
New-NetFirewallRule -DisplayName "IOPaint Web UI" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
```

## 完成後回報

請回報：
1. IOPaint 是否成功啟動？（顯示 "Running on http://0.0.0.0:8080"）
2. 端口 8080 是否在監聽？（`netstat -ano | Select-String ":8080.*LISTENING"`）
3. 本地訪問是否成功？（StatusCode 應該是 200）
4. 有任何錯誤訊息嗎？

如果成功，Mac 端應該可以訪問 http://100.107.71.38:8080

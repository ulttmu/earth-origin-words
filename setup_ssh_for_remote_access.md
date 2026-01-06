# 設置 SSH 遠端訪問 - 給 Windows PC Claude

我需要讓 Mac 端的 Claude 能夠透過 SSH 連入這台 Windows PC 來安裝和配置軟體。

## 系統資訊
- Tailscale IP: 100.107.71.38
- Tailscale 設備名: desktop-ufeca9k
- Mac 端正在嘗試連接：`tailscale ssh desktop-ufeca9k`

## 需要你執行的任務

### 1. 安裝並啟用 OpenSSH Server

請執行以下 PowerShell 指令（以管理員權限）：

```powershell
# 檢查是否已安裝
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'

# 安裝 OpenSSH Server
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 啟動 SSH 服務
Start-Service sshd

# 設定開機自動啟動
Set-Service -Name sshd -StartupType 'Automatic'

# 確認服務狀態
Get-Service sshd
```

### 2. 配置防火牆規則

```powershell
# 檢查防火牆規則（應該會自動創建）
Get-NetFirewallRule -Name *ssh*

# 如果沒有，手動創建
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

### 3. 配置 SSH 允許從 Tailscale 連入

編輯 SSH 配置文件：`C:\ProgramData\ssh\sshd_config`

確保以下設定：
```
PubkeyAuthentication yes
PasswordAuthentication yes
PermitRootLogin no
```

然後重啟服務：
```powershell
Restart-Service sshd
```

### 4. 檢查當前用戶名

```powershell
whoami
$env:USERNAME
```

### 5. 測試 SSH 本地連接

```powershell
# 測試本地 SSH
ssh localhost

# 測試 Tailscale IP
ssh 100.107.71.38
```

### 6. 啟用 Tailscale SSH（如果可用）

Tailscale 有內建的 SSH 功能，可以不需要密碼：

```powershell
# 在 Tailscale 中啟用 SSH
tailscale up --ssh
```

## 預期結果

完成後，Mac 端應該可以執行以下命令成功連入：
```bash
# 方式 1: 使用 Tailscale SSH（無需密碼）
tailscale ssh desktop-ufeca9k

# 方式 2: 使用標準 SSH
ssh <用戶名>@100.107.71.38
```

## 請回報

完成後請告訴我：
1. OpenSSH Server 是否成功啟動？
2. 當前 Windows 用戶名是什麼？
3. `ssh localhost` 是否可以連接？
4. `tailscale up --ssh` 是否執行成功？
5. 有沒有任何錯誤訊息？

## 備註

設置完成後，Mac 端的 Claude 就可以：
- 遠端安裝 IOPaint
- 配置批次處理腳本
- 管理 ComfyUI 和其他工具
- 無需人工介入執行各種安裝和配置任務

# SSH 連接診斷和修復 - 給 Windows PC Claude

Mac 端仍然無法連接，需要診斷並修復。

## 診斷步驟

### 1. 檢查 authorized_keys 文件

```powershell
# 檢查文件是否存在
$authFile = "$env:USERPROFILE\.ssh\authorized_keys"
Write-Host "文件路徑: $authFile"
Write-Host "是否存在: $(Test-Path $authFile)"

# 顯示內容
Write-Host "`n=== authorized_keys 內容 ==="
Get-Content $authFile

# 檢查權限
Write-Host "`n=== 文件權限 ==="
Get-Acl $authFile | Select-Object Owner, AccessToString
```

### 2. 檢查 SSH 配置文件

```powershell
# 檢查 sshd_config
$sshdConfig = "C:\ProgramData\ssh\sshd_config"
Write-Host "`n=== SSH 配置 ==="
Get-Content $sshdConfig | Select-String -Pattern "PubkeyAuthentication|PasswordAuthentication|AuthorizedKeysFile"
```

### 3. 修復權限（重要！）

Windows OpenSSH 對 authorized_keys 權限要求很嚴格：

```powershell
# 完全重置權限
$authFile = "$env:USERPROFILE\.ssh\authorized_keys"

# 禁用繼承
icacls $authFile /inheritance:r

# 只給當前用戶和 SYSTEM 完全控制
icacls $authFile /grant "${env:USERNAME}:F"
icacls $authFile /grant "SYSTEM:F"

# 確認權限
Write-Host "`n=== 修復後的權限 ==="
icacls $authFile
```

### 4. 檢查 SSH 配置文件中的 authorized_keys 路徑

確保 `sshd_config` 沒有被註釋掉：

```powershell
# 編輯配置文件
$sshdConfig = "C:\ProgramData\ssh\sshd_config"

# 檢查並確保以下行存在且未被註釋
$requiredLines = @(
    "PubkeyAuthentication yes",
    "AuthorizedKeysFile .ssh/authorized_keys"
)

foreach ($line in $requiredLines) {
    Write-Host "檢查: $line"
    $exists = Get-Content $sshdConfig | Select-String -Pattern $line
    if ($exists) {
        Write-Host "  ✅ 已存在"
    } else {
        Write-Host "  ❌ 缺失或被註釋"
    }
}
```

### 5. 檢查 administrators_authorized_keys

Windows 特殊情況：如果用戶是管理員，可能需要檢查另一個文件：

```powershell
$adminAuthFile = "C:\ProgramData\ssh\administrators_authorized_keys"
if (Test-Path $adminAuthFile) {
    Write-Host "`n⚠️  發現 administrators_authorized_keys"
    Write-Host "如果當前用戶是管理員，需要將公鑰也加入這個文件："

    $publicKey = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDXmeIVcBEIj/frhqtp/pqp966fhxR6ywabQ1Evmc/wo claude-code"
    Add-Content -Path $adminAuthFile -Value $publicKey

    # 設置權限
    icacls $adminAuthFile /inheritance:r
    icacls $adminAuthFile /grant "BUILTIN\Administrators:F"
    icacls $adminAuthFile /grant "SYSTEM:F"

    Write-Host "已將公鑰加入 administrators_authorized_keys"
}
```

### 6. 重啟 SSH 服務並查看日誌

```powershell
# 重啟服務
Restart-Service sshd
Write-Host "SSH 服務已重啟"

# 檢查服務狀態
Get-Service sshd | Select-Object Status, StartType

# 查看最近的 SSH 日誌
Write-Host "`n=== SSH 日誌（最近 10 條）==="
Get-WinEvent -LogName "OpenSSH/Operational" -MaxEvents 10 | Select-Object TimeCreated, Message | Format-List
```

## 完整修復腳本（一鍵執行）

```powershell
# 完整的 SSH 公鑰修復腳本
Write-Host "開始修復 SSH 公鑰認證..." -ForegroundColor Cyan

# 1. 確保目錄存在
$sshDir = "$env:USERPROFILE\.ssh"
New-Item -ItemType Directory -Force -Path $sshDir | Out-Null

# 2. 寫入公鑰
$publicKey = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDXmeIVcBEIj/frhqtp/pqp966fhxR6ywabQ1Evmc/wo claude-code"
$authFile = "$sshDir\authorized_keys"
Set-Content -Path $authFile -Value $publicKey -Force

# 3. 修復權限
icacls $authFile /inheritance:r
icacls $authFile /grant "${env:USERNAME}:F"
icacls $authFile /grant "SYSTEM:F"

# 4. 檢查是否為管理員
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Write-Host "檢測到管理員用戶，同時設置 administrators_authorized_keys..." -ForegroundColor Yellow
    $adminAuthFile = "C:\ProgramData\ssh\administrators_authorized_keys"
    Set-Content -Path $adminAuthFile -Value $publicKey -Force
    icacls $adminAuthFile /inheritance:r
    icacls $adminAuthFile /grant "BUILTIN\Administrators:F"
    icacls $adminAuthFile /grant "SYSTEM:F"
}

# 5. 重啟 SSH
Restart-Service sshd

Write-Host "`n✅ 修復完成" -ForegroundColor Green
Write-Host "authorized_keys 內容:"
Get-Content $authFile
Write-Host "`n權限:"
icacls $authFile
```

## 請回報

執行完整修復腳本後，請回報：
1. authorized_keys 的內容
2. icacls 顯示的權限
3. 是否為管理員用戶
4. SSH 服務狀態

完成後 Mac 端會再次測試連接。

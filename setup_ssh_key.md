# 設置 SSH 公鑰認證 - 給 Windows PC Claude

Mac 端 Claude 需要免密碼 SSH 訪問。請幫我將以下公鑰加入到 Windows 的 SSH authorized_keys。

## Mac 端的 SSH 公鑰

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDXmeIVcBEIj/frhqtp/pqp966fhxR6ywabQ1Evmc/wo claude-code
```

## 執行步驟

### 1. 創建 .ssh 目錄（如果不存在）

```powershell
# 在用戶目錄下創建 .ssh 資料夾
$sshPath = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $sshPath)) {
    New-Item -ItemType Directory -Path $sshPath
}
```

### 2. 將公鑰加入 authorized_keys

```powershell
# Mac 端的公鑰
$publicKey = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDXmeIVcBEIj/frhqtp/pqp966fhxR6ywabQ1Evmc/wo claude-code"

# 加入到 authorized_keys
$authorizedKeysPath = "$env:USERPROFILE\.ssh\authorized_keys"
Add-Content -Path $authorizedKeysPath -Value $publicKey

# 顯示內容確認
Write-Host "已加入公鑰到: $authorizedKeysPath"
Get-Content $authorizedKeysPath
```

### 3. 設置正確的權限（重要！）

```powershell
# 修復 authorized_keys 權限
$authorizedKeysPath = "$env:USERPROFILE\.ssh\authorized_keys"

# 移除繼承權限
$acl = Get-Acl $authorizedKeysPath
$acl.SetAccessRuleProtection($true, $false)

# 只允許當前用戶和 SYSTEM 訪問
$userRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $env:USERNAME, "FullControl", "Allow"
)
$systemRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "SYSTEM", "FullControl", "Allow"
)

$acl.SetAccessRule($userRule)
$acl.SetAccessRule($systemRule)
Set-Acl $authorizedKeysPath $acl

Write-Host "權限設置完成"
```

### 4. 重啟 SSH 服務

```powershell
Restart-Service sshd
Write-Host "SSH 服務已重啟"
```

### 5. 測試配置

```powershell
# 檢查 authorized_keys 是否存在
Test-Path "$env:USERPROFILE\.ssh\authorized_keys"

# 檢查權限
Get-Acl "$env:USERPROFILE\.ssh\authorized_keys" | Format-List

# 檢查 SSH 服務狀態
Get-Service sshd
```

## 預期結果

完成後，Mac 端應該可以執行以下命令**無需密碼**連入：
```bash
ssh user@100.107.71.38
```

## 請回報

執行完成後請告訴我：
1. authorized_keys 是否成功創建？
2. 公鑰是否已加入？（顯示 Get-Content 的結果）
3. 權限是否正確設置？
4. SSH 服務是否重啟成功？

完成後 Mac 端會立即測試連接。

# ============================================================
#  给 CppVideoLearner 加一个本机自签名身份，让 SmartScreen 不再拦
#
#  用法（必须管理员）：
#    1. 右键「Windows PowerShell」→「以管理员身份运行」
#    2. cd 到项目根目录：  cd D:\ds-work\CppVideoLearner
#    3. 执行：  powershell -ExecutionPolicy Bypass -File .\tools\sign-app.ps1
#
#  它做四件事：
#    1. 生成一张代码签名证书（只留在本机，私钥不出机器）
#    2. 把证书导入「受信任的根证书颁发机构」（这一步需要管理员）
#    3. 给绿色版和单文件版的 exe 签名
#    4. 回读签名状态确认成功
#
#  以后重新打包，exe 会被覆盖、签名丢失，再跑一次本脚本即可
#  （证书会复用，不会重复创建）。
# ============================================================

$ErrorActionPreference = 'Stop'

# ---------- 0. 管理员检查 ----------
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host ""
    Write-Host "需要管理员权限。请右键 PowerShell 选择「以管理员身份运行」后重试。" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
Write-Host "[1/5] 管理员权限 OK" -ForegroundColor Green

# ---------- 1. 定位 exe ----------
$candidates = @(
    "D:\ds-work\CppVideoLearner\release\win-unpacked\CppVideoLearner.exe",
    "D:\ds-work\CppVideoLearner\release\CppVideoLearner.exe"
)
$targets = @()
foreach ($c in $candidates) {
    if (Test-Path $c) { $targets += $c }
}

if ($targets.Count -eq 0) {
    Write-Host "找不到要签名的 exe，请先执行 pnpm run build 打包。" -ForegroundColor Red
    exit 1
}
Write-Host "[2/5] 待签名文件:"
foreach ($t in $targets) { Write-Host "        $t" }

# ---------- 2. 证书 ----------
$subject = "CN=CppVideoLearner (self-signed)"
$cert = $null

$existing = Get-ChildItem Cert:\CurrentUser\My -ErrorAction SilentlyContinue
foreach ($c in $existing) {
    if ($c.Subject -eq $subject -and $c.HasPrivateKey) {
        $cert = $c
        break
    }
}

if ($cert -ne $null) {
    Write-Host "[3/5] 复用已有证书: $($cert.Thumbprint)" -ForegroundColor Green
} else {
    Write-Host "[3/5] 创建代码签名证书..."
    $params = @{
        Type               = 'CodeSigningCert'
        Subject            = $subject
        KeyUsage           = 'DigitalSignature'
        KeyExportPolicy    = 'Exportable'
        KeyAlgorithm       = 'RSA'
        KeyLength          = 3072
        HashAlgorithm      = 'SHA256'
        CertStoreLocation  = 'Cert:\CurrentUser\My'
        NotAfter           = (Get-Date).AddYears(10)
    }
    $cert = New-SelfSignedCertificate @params
    Write-Host "      证书已创建: $($cert.Thumbprint)" -ForegroundColor Green
}

# ---------- 3. 导入受信任根 ----------
$inRoot = $false
$roots = Get-ChildItem Cert:\LocalMachine\Root -ErrorAction SilentlyContinue
foreach ($r in $roots) {
    if ($r.Thumbprint -eq $cert.Thumbprint) { $inRoot = $true; break }
}

if ($inRoot) {
    Write-Host "[4/5] 证书已在受信任根中" -ForegroundColor Green
} else {
    Write-Host "[4/5] 导入到受信任的根证书颁发机构..."
    $cerPath = Join-Path $env:TEMP "CppVideoLearner.cer"
    Export-Certificate -Cert $cert -FilePath $cerPath -Type CERT | Out-Null
    Import-Certificate -FilePath $cerPath -CertStoreLocation 'Cert:\LocalMachine\Root' | Out-Null
    Remove-Item $cerPath -Force -ErrorAction SilentlyContinue
    Write-Host "      已导入" -ForegroundColor Green
}

# ---------- 4. 签名 ----------
Write-Host "[5/5] 签名..."
foreach ($exe in $targets) {
    $name = Split-Path -Leaf $exe
    try {
        $r = Set-AuthenticodeSignature -FilePath $exe -Certificate $cert -HashAlgorithm SHA256
        if ($r.Status -eq 'Valid') {
            Write-Host "      $name -> 签名成功" -ForegroundColor Green
        } else {
            Write-Host "      $name -> $($r.Status) : $($r.StatusMessage)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "      $name -> 失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ---------- 5. 回读验证 ----------
Write-Host ""
Write-Host "=== 验证结果 ===" -ForegroundColor Cyan
foreach ($exe in $targets) {
    $sig = Get-AuthenticodeSignature $exe
    Write-Host ("  {0}" -f (Split-Path -Leaf $exe))
    Write-Host ("    状态   : {0}" -f $sig.Status)
    Write-Host ("    签署者 : {0}" -f $sig.SignerCertificate.Subject)
}

Write-Host ""
Write-Host "完成。现在从桌面快捷方式再启动一次试试。" -ForegroundColor Green
Write-Host "如果仍然弹提示，说明 SmartScreen 对自签名证书也保留云信誉判定。" -ForegroundColor Yellow
Write-Host "那种情况只能关闭「检查应用和文件」，或者直接用浏览器版（无 exe）。" -ForegroundColor Yellow

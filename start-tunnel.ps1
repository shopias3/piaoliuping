# 漂流瓶 App - cloudflared 外网隧道启动脚本（灯塔同款）
# 启动后把公网 URL 写入 .temp\cloudflared_url.txt，供桌面快捷方式读取
$ErrorActionPreference = 'Stop'
$cfd  = 'D:\runtime\cloudflared\cloudflared.exe'
$errLog = 'D:\piaoliuping\backend\tunnel.err.log'
$outLog = 'D:\piaoliuping\backend\tunnel.out.log'
$dir  = 'D:\piaoliuping\backend'
$urlFile = 'D:\piaoliuping\.temp\cloudflared_url.txt'

New-Item -ItemType Directory -Path $dir -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path $urlFile) -Force | Out-Null

# 已存在指向 8010 的隧道则跳过
$existing = Get-CimInstance Win32_Process -Filter "Name='cloudflared.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like '*127.0.0.1:8010*' }

if (-not $existing) {
    Start-Process -FilePath $cfd -ArgumentList 'tunnel','--url','http://127.0.0.1:8010' `
        -WorkingDirectory $dir -WindowStyle Hidden -RedirectStandardOutput $outLog -RedirectStandardError $errLog
    Write-Output "[start] cloudflared tunnel -> http://127.0.0.1:8010"
} else {
    Write-Output "[skip] tunnel already running (PID $($existing.ProcessId -join ','))"
}

# 等待并写入公网 URL
$deadline = (Get-Date).AddSeconds(40)
$found = $false
while ((Get-Date) -lt $deadline) {
    if (Test-Path $errLog) {
        $c = Get-Content $errLog -Raw -ErrorAction SilentlyContinue
        if ($c -match 'https://[a-z0-9-]+\.trycloudflare\.com') { $found = $true; break }
    }
    Start-Sleep -Seconds 2
}

if ($found) {
    [System.IO.File]::WriteAllText($urlFile, $Matches[0], [System.Text.Encoding]::ASCII)
    Write-Output "PUBLIC_URL=$($Matches[0])"
} else {
    Write-Output '[warn] 未能获取公网 URL，请稍后查看 tunnel.err.log'
}
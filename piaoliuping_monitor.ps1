# 漂流瓶 App - 服务守护脚本（灯塔同款机制）
# 每 30 秒巡检：后端 8010 挂了自动拉起；隧道挂了自动重建并更新公网 URL
$BackendPort = 8010
$CheckInterval = 30

try { [System.Net.WebRequest]::DefaultWebProxy = $null } catch {}

$PyExe = "D:\piaoliuping\backend\.venv\Scripts\python.exe"
$BackendDir = "D:\piaoliuping\backend"
$CloudflaredExe = "D:\runtime\cloudflared\cloudflared.exe"
$UrlFile = "D:\piaoliuping\.temp\cloudflared_url.txt"
$TunnelErr = "D:\piaoliuping\backend\tunnel.err.log"
$TunnelOut = "D:\piaoliuping\backend\tunnel.out.log"
$LogFile = "D:\piaoliuping\backend\monitor.log"

function WriteLog($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Value "[$ts] $msg" -Encoding UTF8
}

function GetProcessOnPort($port) {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conn) { return $conn[0].OwningProcess } else { return $null }
}

function StopProcessOnPort($port) {
    $procId = GetProcessOnPort $port
    if ($procId) { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue }
}

function RestartBackend {
    StopProcessOnPort $BackendPort
    Start-Sleep -Seconds 2
    try {
        Start-Process -FilePath $PyExe -ArgumentList "-m","uvicorn","app.main:app","--host","0.0.0.0","--port","8010" -WorkingDirectory $BackendDir -WindowStyle Hidden
        WriteLog "Backend(8010) restarted"
    } catch {
        WriteLog "Backend(8010) restart FAILED: $_"
    }
}

function GetTunnelUrl {
    foreach ($f in $TunnelOut, $TunnelErr) {
        if (Test-Path $f) {
            $m = Select-String -Path $f -Pattern 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($m) { return $m.Matches[0].Value }
        }
    }
    return $null
}

function RestartTunnel {
    Get-CimInstance Win32_Process -Filter "Name='cloudflared.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*127.0.0.1:8010*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
    Remove-Item $TunnelOut, $TunnelErr -ErrorAction SilentlyContinue
    try {
        Start-Process -FilePath $CloudflaredExe -ArgumentList "tunnel","--url","http://127.0.0.1:8010" -WorkingDirectory $BackendDir -WindowStyle Hidden -RedirectStandardOutput $TunnelOut -RedirectStandardError $TunnelErr
        Start-Sleep -Seconds 8
        $url = GetTunnelUrl
        if ($url) {
            [System.IO.File]::WriteAllText($UrlFile, $url, [System.Text.Encoding]::ASCII)
            WriteLog "Tunnel(8010) restarted: $url"
        } else {
            WriteLog "Tunnel(8010) restarted (URL not captured yet)"
        }
    } catch {
        WriteLog "Tunnel(8010) restart FAILED: $_"
    }
}

# 单实例防重（用锁文件，避免命令行自匹配误判）
$LockFile = "D:\piaoliuping\backend\monitor.lock"
$myPid = $PID
$otherPid = $null
if (Test-Path $LockFile) {
    $otherPid = (Get-Content $LockFile -ErrorAction SilentlyContinue | Select-Object -First 1)
}
if ($otherPid) {
    $alive = Get-CimInstance Win32_Process -Filter "ProcessId=$otherPid" -ErrorAction SilentlyContinue
    if ($alive -and $alive.ProcessId -ne $myPid) {
        WriteLog "Another piaoliuping_monitor instance running (PID=$otherPid), exiting."
        exit 0
    }
}
Set-Content -Path $LockFile -Value $myPid -Encoding ASCII

WriteLog "========== Piaoliuping Service Monitor Started =========="

while ($true) {
    # 后端
    try {
        $bePid = GetProcessOnPort $BackendPort
        if ($bePid) {
            WriteLog "Backend(8010) OK PID=$bePid"
        } else {
            WriteLog "Backend(8010) not running, starting..."
            RestartBackend
        }
    } catch { WriteLog "Backend(8010) check error: $_" }

    # 隧道
    try {
        if (Test-Path $CloudflaredExe) {
            $cfProc = Get-CimInstance Win32_Process -Filter "Name='cloudflared.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*127.0.0.1:8010*' }
            if ($cfProc) {
                WriteLog "Tunnel(8010) OK PID=$($cfProc[0].ProcessId)"
                $u = GetTunnelUrl
                if ($u) {
                    $old = if (Test-Path $UrlFile) { (Get-Content $UrlFile -ErrorAction SilentlyContinue | Select-Object -First 1) } else { $null }
                    if ($u -ne $old) { [System.IO.File]::WriteAllText($UrlFile, $u, [System.Text.Encoding]::ASCII); WriteLog "Tunnel URL captured: $u" }
                }
            } else {
                WriteLog "Tunnel(8010) not running, starting..."
                RestartTunnel
            }
        }
    } catch { WriteLog "Tunnel(8010) check error: $_" }

    WriteLog "Next check in ${CheckInterval}s..."
    Start-Sleep -Seconds $CheckInterval
}
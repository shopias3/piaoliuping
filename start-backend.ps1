# 漂流瓶 App - 后端启动脚本（FastAPI, 端口 8010）
$ErrorActionPreference = 'Stop'

# 防重复：若 8010 已在监听则跳过（用于计划任务自启）
if (Get-NetTCPConnection -LocalPort 8010 -State Listen -ErrorAction SilentlyContinue) {
    Write-Host '[skip] backend already running on 8010'
    exit 0
}

Set-Location 'D:\piaoliuping\backend'

if (-not (Test-Path '.\.venv\Scripts\python.exe')) {
    Write-Host '[init] 创建虚拟环境并安装依赖...'
    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
}

Write-Host '[run] 启动后端 http://0.0.0.0:8010（本机 http://127.0.0.1:8010 ，同端口托管 H5 界面+接口）'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8010

# 漂流瓶 App - 前端启动脚本（uni-app H5, 端口 5173）
$ErrorActionPreference = 'Stop'
Set-Location 'D:\piaoliuping\frontend'

if (-not (Test-Path '.\node_modules')) {
    Write-Host '[init] 安装前端依赖（首次较慢）...'
    npm install --registry=https://registry.npmmirror.com --no-audit --no-fund
}

Write-Host '[run] 启动前端 http://127.0.0.1:5173/  (API 代理到 8010)'
npm run dev:h5

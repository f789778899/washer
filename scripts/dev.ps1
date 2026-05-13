$ErrorActionPreference = "Stop"

$root = Resolve-Path "$PSScriptRoot\.."

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\backend'; python -m pip install -e .; docflow-api"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\frontend'; npm install; npm run dev"

Write-Host "Backend and frontend dev servers started."


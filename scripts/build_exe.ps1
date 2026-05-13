$ErrorActionPreference = "Stop"

$root = Resolve-Path "$PSScriptRoot\.."
$frontend = Join-Path $root "frontend"
$backend = Join-Path $root "backend"
$spec = Join-Path $root "desktop\docflow_studio.spec"

Push-Location $frontend
npm install
npm run build
Pop-Location

Push-Location $backend
python -m pip install -e ".[dev]"
Pop-Location

pyinstaller --noconfirm $spec

Write-Host ""
Write-Host "Build completed. EXE output:"
Write-Host (Join-Path $root "dist\DocFlowStudio\DocFlowStudio.exe")


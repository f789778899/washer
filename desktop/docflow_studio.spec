# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

repo_root = Path.cwd()
backend_src = repo_root / "backend" / "src"
launcher_script = repo_root / "desktop" / "launcher.py"
frontend_dist = repo_root / "frontend" / "dist"
config_dir = repo_root / "config"

datas = []
if frontend_dist.exists():
    datas.append((str(frontend_dist), "frontend/dist"))
datas.append((str(config_dir), "config"))

hiddenimports = [
    "docflow",
    "docflow.api.app",
    "docflow.desktop_launcher",
    "docflow.mcp.server",
]

a = Analysis(
    [str(launcher_script)],
    pathex=[str(backend_src)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="DocFlowStudio",
    debug=False,
    strip=False,
    upx=True,
    console=False,
)

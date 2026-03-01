# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_app.py'],
    pathex=[],
    binaries=[],
    datas=[('modules', 'modules'), ('db_manager.py', '.')],
    hiddenimports=['modules.building', 'modules.curing', 'modules.qc', 'modules.despatch', 'modules.lab', 'modules.crm', 'modules.admin_dashboard', 'modules.global_dashboard', 'modules.production_log', 'reportlab', 'reportlab.pdfgen.canvas', 'reportlab.lib.pagesizes'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SmartFactory_OS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

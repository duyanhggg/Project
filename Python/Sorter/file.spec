# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['E:\\Code\\Python\\file.pyw'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['infi.systray', 'plyer', 'plyer.platforms.win.notification', 'plyer.platforms.win.toast', 'win32com', 'winshell', 'win10toast'],
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
    name='file',
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

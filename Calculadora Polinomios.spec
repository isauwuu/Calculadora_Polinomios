# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

# ``gui.controlador`` importa los métodos con importlib.import_module, por lo
# que PyInstaller no puede descubrirlos solo. Hay que incluirlos explícitamente
# o el .exe abre pero responde "Método aún no disponible".
hiddenimports = (
    collect_submodules("core")
    + collect_submodules("metodos")
    + collect_submodules("gui")
    + collect_submodules("gui.pestanas")
)

datas = [("mi_icono.ico", ".")]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='Calculadora Polinomios',
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
    icon=['mi_icono.ico'],
)

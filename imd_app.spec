# -*- mode: python ; coding: utf-8 -*-
# Archivo de especificación para PyInstaller - IMD Material Control

import os

# Obtener el directorio del proyecto
project_dir = os.path.abspath('.')

# Análisis de la aplicación principal
a = Analysis(
    ['imd_desktop_main.py'],
    pathex=[project_dir],
    binaries=[],
    datas=[
        # Incluir archivos de datos necesarios
        ('imd_desktop_app.html', '.'),
        ('config.py', '.'),
        ('icono_app.png', '.'),
    ],
    hiddenimports=[
        # Módulos que PyInstaller podría no detectar automáticamente
        'mysql.connector',
        'flask',
        'flask_cors',
        'requests',
        'webview',
        'threading',
        'socket',
        'logging',
        'datetime',
        'json',
        'sys',
        'os',
        'time'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Excluir módulos innecesarios para reducir tamaño
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'pygame',
        'wx'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Archivos de Python compilados
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Ejecutable principal
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='IMD_MaterialControl',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icono_app.png' if os.path.exists('icono_app.png') else None,  # Icono de la aplicación
    version_file='version_info.txt' if os.path.exists('version_info.txt') else None
)
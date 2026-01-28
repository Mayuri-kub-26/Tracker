# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

# Base path of the repository
base_path = os.path.abspath(os.getcwd())

# List of scripts to bundle
scripts = [
    os.path.join('src', 'main.py')
]

# Analysis for the main tracker app
a = Analysis(
    scripts,
    pathex=[base_path],
    binaries=[],
    datas=[
        ('VERSION', '.'),
        ('src/config.yaml', 'src'),
        # Add models if you want them bundled inside (can make EXE very large)
        # ('models/*.onnx', 'models'), 
    ],
    hiddenimports=[
        'cv2',
        'yaml',
        'requests',
        'src.core.config',
        'src.core.app',
        'src.hardware.camera',
        'src.hardware.gimbal',
        'src.detection.detector',
        'src.detection.tracker',
        'src.utils.visualization',
        'src.utils.logger',
        'src.utils.paths'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TrackerApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to False if you don't want a console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None, # Path to an .ico file if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TrackerApp',
)

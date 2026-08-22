# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# Read version from single source
exec(open('version.py').read())

# MediaPipe bundling — collect TFLite models, DLLs, and metadata
mediapipe_datas = collect_data_files('mediapipe')
mediapipe_binaries = collect_dynamic_libs('mediapipe')

# Also collect OpenCV data (haar cascades not used, but safe to include)
try:
    cv2_datas = collect_data_files('cv2')
except Exception:
    cv2_datas = []

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=mediapipe_binaries,
    datas=[
        ('hand_landmarker.task', '.'),
    ] + mediapipe_datas + cv2_datas,
    hiddenimports=[
        'mediapipe.tasks.python',
        'mediapipe.tasks.python.vision',
        'mediapipe.tasks.python.components.containers.landmark',
        '_tkinter',           # for error/update dialogs
        'tkinter',
        'tkinter.messagebox',
        'tkinter.ttk',
        'matplotlib',
        'matplotlib.backends',
        'matplotlib.backends.backend_agg',
        'matplotlib.backends.backend_tkagg',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pandas',
        'scipy',
        'sklearn',
        'torch',
        'tensorflow',
        'jupyter',
        'notebook',
        'IPython',
        'sounddevice',        # unused transitive dep from mediapipe; avoid PortAudio warning
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# Linux onedir bundle: EXE produces dist/HandFilter/HandFilter (the executable)
# COLLECT then adds binaries/datas alongside it in the same directory
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='HandFilter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                 # UPX breaks MediaPipe TFLite kernels / compiled graphs
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,             # windowed app; errors go to tkinter dialogs
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# For Linux onedir, COLLECT bundles everything into dist/HandFilter/
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='HandFilter',
)
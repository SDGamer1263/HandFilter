#!/usr/bin/env python3
"""Sync version.py -> installer/version.iss + version_info.txt (for PyInstaller EXE metadata)."""
import os
import sys
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import version

VERSION = version.__version__
print(f"Syncing version: {VERSION}")

# --- version_info.txt for PyInstaller (VS_VERSION_INFO resource) ---
# Format: https://pyinstaller.org/en/stable/spec-files.html#version-resource-on-windows
# tuple: (filevers, prodvers, mask, flags, OS, fileType, subtype, lang, codepage)
# filevers/prodvers = (major, minor, patch, build)
parts = VERSION.split('.')
major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
build = 0

version_info_content = f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, {build}),
    prodvers=({major}, {minor}, {patch}, {build}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [
          StringStruct(u'CompanyName', u'SDGamer1263'),
          StringStruct(u'FileDescription', u'HandFilter - Real-time hand tracking with drawing and filters'),
          StringStruct(u'FileVersion', u'{VERSION}'),
          StringStruct(u'InternalName', u'HandFilter'),
          StringStruct(u'LegalCopyright', u'MIT License'),
          StringStruct(u'OriginalFilename', u'HandFilter.exe'),
          StringStruct(u'ProductName', u'HandFilter'),
          StringStruct(u'ProductVersion', u'{VERSION}'),
        ]
      )
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''

version_info_path = os.path.join(ROOT, 'version_info.txt')
with open(version_info_path, 'w', encoding='utf-8') as f:
    f.write(version_info_content)
print(f"Written: {version_info_path}")

# --- installer/version.iss for Inno Setup ---
iss_content = f'#define AppVersion "{VERSION}"\n#define AppVersionMajor {major}\n#define AppVersionMinor {minor}\n#define AppVersionPatch {patch}\n'

installer_dir = os.path.join(ROOT, 'installer')
os.makedirs(installer_dir, exist_ok=True)
iss_path = os.path.join(installer_dir, 'version.iss')
with open(iss_path, 'w', encoding='utf-8') as f:
    f.write(iss_content)
print(f"Written: {iss_path}")

print("Version sync complete.")
# HandFilter Windows Distribution — Progress Tracker

## Milestones

### Phase 0 — Foundation
- [x] Create `version.py` with `__version__ = "1.0.0"`
- [x] Create `PROGRESS.md` checklist

### Phase 1 — Packaging (PyInstaller)
- [x] Rewrite `main.spec`: name, icon, upx=False, MediaPipe collect hooks, hiddenimports, onedir
- [x] `pip install pyinstaller` + `pyinstaller main.spec` succeeds
- [x] `dist/HandFilter/HandFilter.exe` launches → shows camera dialog (not silent crash)
- [x] Verify model + icon bundled in `dist/HandFilter/`

### Phase 2 — Error Dialogs + Resource Bundling
- [x] Create `error_dialog.py` (tkinter: model fail, camera fail retry/close, generic crash)
- [x] Modify `main.py`: try/except wrapper, friendly startup errors
- [x] Rebuild exe → test without webcam → camera dialog with Retry/Close appears

### Phase 3 — Installer (Inno Setup)
- [x] Create `scripts/sync-version.py` → generates `installer/version.iss` + `version_info.txt`
- [x] Create `installer/handfilter.iss` (per-user, AppId stable, Start Menu, optional desktop)
- [x] `iscc installer/handfilter.iss` → `HandFilter-1.0.0-Windows-Setup.exe` (needs Inno Setup installed)
- [x] Silent install test: `/VERYSILENT /CURRENTUSER /NORESTART /SP-`
- [x] Start Menu launch works; uninstall cleans Start Menu (known Inno limitation: app dir remains)

### Phase 4 — Update System
- [x] Create `updater.py` (background thread, GitHub API, semver compare, tkinter dialog)
- [x] Download flow: prune stale temp → download → verify TLS → spawn detached update_launcher.bat
- [x] `update_launcher.bat`: wait 3s → silent install (same AppId) → relaunch → self-delete
- [x] Self-check: version parse + semver compare + installer asset finder verified
- [ ] Live test: real GitHub release newer than 1.0.0 → update dialog → download → install → relaunch

### Phase 5 — README + Visual Docs
- [x] Rewrite `README.md` (user-first: Download CTA, Features, How to Use, Gestures, Screenshots, Troubleshooting, Requirements, Development, License)
- [x] Remove broken screenshot refs (no user captures)
- [x] Add gesture explainer: text table (in README) + compact SVG diagram at `docs/gestures.svg`

### Phase 6 — CI (GitHub Actions)
- [x] Create `.github/workflows/build-windows.yml` (workflow_dispatch + tag push v*)
- [x] Windows-latest, Python 3.11, pyinstaller, zip portable, choco innosetup, iscc
- [x] Upload artifacts: portable zip + setup exe
- [x] Manual release process documented: `gh release create` with artifacts
- [x] Fix CI: detect existing Inno Setup on runner instead of forcing v6.2.2 install (runner has v6.7.1)
- [x] Fix CI: remove Chocolatey Inno Setup install entirely; use ISCC.exe pre-installed on windows-latest with verification step

### Phase 7 — Full Windows Testing
- [x] Source: `python main.py` — all features
- [x] Portable: `HandFilter.exe` from non-source dir — camera, tracking, drawing, filters, gestures, menu, settings, close/reopen
- [x] Installer: install → Start Menu → desktop shortcut → all features → uninstall
- [x] Update failure paths analyzed + code hardening:
    - GitHub/internet down → graceful "check failed" or silent background skip
    - Download fails → "Update Failed" dialog
    - No installer asset in release → "Update Not Ready" dialog (manual fallback)
- [x] No secrets in source (scanned)
- [x] .gitignore updated (release artifacts, test_portable, QA prompts ignored)
- [x] Version consistent: version.py → version.iss → version_info.txt → main.spec (all 1.0.0)

---

**Status Legend**: [ ] pending | [~] in progress | [x] done
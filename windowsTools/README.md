# MouseGhost Windows

Windows build of MouseGhost. This version keeps the macOS project untouched and replaces the platform-specific pieces with Win32 API calls.

## Run from source

```powershell
cd windowsTools
python main.py
```

## Build exe

```powershell
cd windowsTools
python -m PyInstaller MouseGhostWindows.spec --noconfirm
```

The executable is generated at:

```text
windowsTools\dist\MouseGhostWindows.exe
```

Settings are stored in `settings.json` next to the executable after first launch.

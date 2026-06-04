# MouseGhost / AutoNotes

MouseGhost is a desktop automation tool that simulates human-like mouse movement,
occasional scrolling, and Chrome tab switching.

The project currently contains two platform-specific versions:

- macOS version in the project root, built with PyObjC, Cocoa, Quartz, and AppleScript.
- Windows version in `windowsTools/`, redesigned to appear as an AutoNotes note-taking app and built with `tkinter` plus Win32 API calls.

## Repository Layout

```text
.
|-- main.py                    # macOS app entry point
|-- mouse_engine.py            # macOS mouse movement and scroll engine
|-- user_watch.py              # macOS user mouse movement watcher
|-- chrome_control.py          # macOS Chrome tab switching through AppleScript
|-- dopamine_ui.py             # macOS Cocoa UI helpers
|-- settings.py                # settings loader for macOS
|-- settings.json              # default settings
|-- MouseGhost.spec            # macOS PyInstaller spec
|-- windowsTools/
|   |-- main.py                # Windows AutoNotes UI entry point
|   |-- mouse_engine.py        # Windows Win32 mouse movement and scroll engine
|   |-- user_watch.py          # Windows user mouse movement watcher
|   |-- chrome_control.py      # Windows Chrome tab switching through Ctrl+Tab
|   |-- settings.py            # Windows settings loader
|   |-- settings.json          # Windows default settings
|   |-- AutoNotes.spec         # Windows PyInstaller spec
|   `-- dist/autoNotes.exe     # Windows executable output
`-- README.md
```

## Windows AutoNotes

The Windows build lives in `windowsTools/`. Its executable is named
`autoNotes.exe`, and the UI is styled as a note-taking app.

Functional controls:

- Start notes: starts the automation engine.
- Stop notes: stops the automation engine.
- Settings: opens the settings window.
- Close application: exits the app.

Visual-only note app controls:

- New note
- Import audio
- Organize highlights
- Export summary
- Search notes
- Cloud sync

Run from source:

```powershell
cd windowsTools
python main.py
```

Build the Windows executable:

```powershell
cd windowsTools
python -m PyInstaller AutoNotes.spec --noconfirm
```

Output:

```text
windowsTools\dist\autoNotes.exe
```

## macOS MouseGhost

The original macOS version remains in the project root.

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pyobjc pyinstaller
```

Run from source:

```bash
python main.py
```

Build with PyInstaller:

```bash
pyinstaller MouseGhost.spec
```

The macOS app uses Accessibility permissions for mouse control and AppleScript
automation permissions for Chrome tab switching.

## Settings

Both platform versions use the same setting names:

| Key | Description | Value |
| --- | --- | --- |
| `scroll_probability` | Chance of triggering a scroll action | `0` to `1` |
| `scroll_min_interval` | Minimum seconds between scroll actions | integer seconds |
| `tab_probability` | Chance of triggering Chrome tab switching | `0` to `1` |
| `tab_min_interval` | Minimum seconds between tab switches | integer seconds |
| `think_time` | Pause/sleep interval between movement cycles | integer seconds |

Default values:

```json
{
  "scroll_probability": 0.9,
  "scroll_min_interval": 4,
  "tab_probability": 0.4,
  "tab_min_interval": 15,
  "think_time": 30
}
```

For packaged builds, settings are stored next to the executable after launch.

## Notes

- `build/`, `__pycache__/`, and generated runtime settings are ignored.
- The Windows executable is intentionally tracked as `windowsTools/dist/autoNotes.exe`.
- The Windows version avoids extra runtime dependencies by using Python standard library modules and Win32 API calls through `ctypes`.

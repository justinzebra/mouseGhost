# MouseGhost / AutoNotes

MouseGhost 是一個桌面自動化工具，用來模擬類似真人的滑鼠移動、偶爾滾動頁面，以及切換 Google Chrome 分頁。

目前專案包含兩個平台版本：

- macOS 版：放在專案根目錄，使用 PyObjC、Cocoa、Quartz 與 AppleScript。
- Windows 版：放在 `windowsTools/`，外觀改成 AutoNotes 筆記 App，使用 `tkinter` 與 Win32 API。

## 專案結構

```text
.
|-- main.py                    # macOS App 入口
|-- mouse_engine.py            # macOS 滑鼠移動與滾輪引擎
|-- user_watch.py              # macOS 使用者滑鼠移動監聽
|-- chrome_control.py          # macOS 透過 AppleScript 切換 Chrome 分頁
|-- dopamine_ui.py             # macOS Cocoa UI 輔助元件
|-- settings.py                # macOS 設定檔讀寫
|-- settings.json              # 預設設定
|-- MouseGhost.spec            # macOS PyInstaller 打包設定
|-- windowsTools/
|   |-- main.py                # Windows AutoNotes UI 入口
|   |-- mouse_engine.py        # Windows Win32 滑鼠移動與滾輪引擎
|   |-- user_watch.py          # Windows 使用者滑鼠移動監聽
|   |-- chrome_control.py      # Windows 透過 Ctrl+Tab 切換 Chrome 分頁
|   |-- settings.py            # Windows 設定檔讀寫
|   |-- settings.json          # Windows 預設設定
|   |-- AutoNotes.spec         # Windows PyInstaller 打包設定
|   `-- dist/autoNotes.exe     # Windows 執行檔輸出
`-- README.md
```

## Windows AutoNotes

Windows 版位於 `windowsTools/`。執行檔名稱為 `autoNotes.exe`，介面偽裝成 AutoNotes 筆記 App。

主要功能按鈕：

- `開始筆記`：啟動自動化引擎。
- `停止筆記`：停止自動化引擎。
- `設定`：開啟設定視窗。
- `關閉應用程式`：關閉 App。

僅作為外觀使用的筆記 App 按鈕：

- `新增筆記`
- `匯入錄音`
- `整理重點`
- `匯出摘要`
- `搜尋筆記`
- `同步雲端`

從原始碼執行：

```powershell
cd windowsTools
python main.py
```

打包 Windows 執行檔：

```powershell
cd windowsTools
python -m PyInstaller AutoNotes.spec --noconfirm
```

輸出位置：

```text
windowsTools\dist\autoNotes.exe
```

## macOS MouseGhost

原始 macOS 版本保留在專案根目錄。

安裝依賴：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pyobjc pyinstaller
```

從原始碼執行：

```bash
python main.py
```

使用 PyInstaller 打包：

```bash
pyinstaller MouseGhost.spec
```

macOS 版需要系統「輔助使用」權限來控制滑鼠，也需要 AppleScript 自動化權限來操作 Chrome。

## 設定

兩個平台版本使用相同的設定名稱：

| Key | 說明 | 數值 |
| --- | --- | --- |
| `scroll_probability` | 觸發滾動動作的機率 | `0` 到 `1` |
| `scroll_min_interval` | 兩次滾動之間的最短秒數 | 整數秒 |
| `tab_probability` | 觸發 Chrome 分頁切換的機率 | `0` 到 `1` |
| `tab_min_interval` | 兩次分頁切換之間的最短秒數 | 整數秒 |
| `think_time` | 每輪移動之間的暫停秒數 | 整數秒 |

預設值：

```json
{
  "scroll_probability": 0.9,
  "scroll_min_interval": 4,
  "tab_probability": 0.4,
  "tab_min_interval": 15,
  "think_time": 30
}
```

打包後的版本會在執行檔旁邊儲存執行時設定檔。

## 注意事項

- `build/`、`__pycache__/` 與執行時產生的 settings 檔案會被忽略。
- Windows 執行檔會追蹤在 `windowsTools/dist/autoNotes.exe`。
- Windows 版盡量避免額外 runtime 依賴，主要使用 Python 標準庫與 `ctypes` 呼叫 Win32 API。

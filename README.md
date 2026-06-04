# MouseGhost

MouseGhost 是一個 macOS 桌面小工具，透過 PyObjC 與 Quartz 模擬滑鼠移動、滾動頁面，並可隨機切換 Google Chrome 分頁。它提供一個簡單的控制視窗，可以開始、停止自動動作，也能調整滾動、切分頁與停頓時間等參數。

> 請只在你有權使用的電腦與情境中執行。這個工具會控制滑鼠、監聽滑鼠移動，並透過 AppleScript 操作 Chrome。

## 功能

- 啟動或停止自動滑鼠移動。
- 使用貝茲曲線與隨機抖動模擬較自然的滑鼠軌跡。
- 隨機執行頁面滾動。
- 隨機切換 Google Chrome 目前前景視窗中的分頁。
- 偵測到使用者移動滑鼠時，自動暫停一段時間。
- 透過設定視窗調整：
  - 滾動機率
  - 滾動最小間隔
  - 切分頁機率
  - 切分頁最小間隔
  - 思考時間 / 暫停時間
- 支援 PyInstaller 打包成 macOS `.app`。

## 專案結構

```text
.
├── main.py              # App 入口、主視窗、設定視窗
├── mouse_engine.py      # 滑鼠移動、滾動、主循環
├── user_watch.py        # 監聽使用者滑鼠移動並觸發暫停
├── chrome_control.py    # 透過 AppleScript 切換 Chrome 分頁
├── dopamine_ui.py       # PyObjC UI 元件與背景樣式
├── settings.py          # 設定檔讀寫
├── settings.json        # 實際設定值
├── MouseGhost.spec      # PyInstaller MouseGhost 打包設定
├── AutoNotes.spec       # PyInstaller AutoNotes 打包設定
├── 主題.png             # 預設背景圖
├── 主題1.png            # 啟動狀態背景圖
├── 主題2.png            # 停止狀態背景圖
├── build/               # PyInstaller 建置暫存輸出
└── dist/                # PyInstaller 打包成品
```

## 系統需求

- macOS
- Python 3.12 或相容版本
- Google Chrome，若需要使用隨機切換分頁功能
- Python 套件：
  - `pyobjc`
  - `pyinstaller`，只有打包時需要

## 安裝

建議先建立虛擬環境：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pyobjc pyinstaller
```

目前專案沒有 `requirements.txt`，若要固定依賴版本，可以之後補上。

## 執行

從原始碼啟動：

```bash
python main.py
```

開啟後會出現 `Mouse Ghost` 視窗：

- `開始偷懶`：啟動自動滑鼠、滾動與分頁切換。
- `停止偷懶`：停止自動行為。
- `設定`：開啟參數控制台。
- `關閉`：停止監聽並結束 App。

## macOS 權限

第一次執行時，macOS 可能會阻擋滑鼠控制、事件監聽或 AppleScript 操作。若功能沒有反應，請到：

```text
系統設定 > 隱私權與安全性
```

確認執行程式已允許下列權限：

- 輔助使用：允許控制滑鼠與監聽輸入事件。
- 自動化：允許操作 Google Chrome。
- 輸入監控：若事件監聽無法正常運作，可能也需要開啟。

如果是從終端機執行 `python main.py`，通常需要授權目前使用的 Terminal、iTerm 或 IDE。若是執行打包後的 `.app`，則需要授權該 App。

## 設定檔

設定值儲存在 `settings.json`。原始碼模式下，檔案位於專案根目錄；PyInstaller `.app` 模式下，設定檔會儲存在執行檔旁邊。

目前支援的設定：

| 欄位 | 說明 | 範圍 / 型別 |
| --- | --- | --- |
| `scroll_probability` | 每輪觸發滾動的機率 | `0` 到 `1` |
| `scroll_min_interval` | 兩次滾動之間的最小秒數 | 整數秒 |
| `tab_probability` | 每輪觸發切換 Chrome 分頁的機率 | `0` 到 `1` |
| `tab_min_interval` | 兩次切換分頁之間的最小秒數 | 整數秒 |
| `think_time` | 每次移動後的等待秒數；使用者移動滑鼠時也會暫停這段時間 | 整數秒 |

預設值定義在 `settings.py`：

```python
DEFAULT = {
    "scroll_probability": 0.9,
    "scroll_min_interval": 4,
    "tab_probability": 0.4,
    "tab_min_interval": 15,
    "think_time": 30
}
```

## 打包

使用 `MouseGhost.spec` 打包：

```bash
pyinstaller MouseGhost.spec
```

或使用目前已有的 `AutoNotes.spec` 打包：

```bash
pyinstaller AutoNotes.spec
```

打包完成後，成品會出現在：

```text
dist/
```

`spec` 檔已將 `主題.png`、`主題1.png`、`主題2.png` 加入打包資料，因此 `.app` 執行時可以正常載入背景圖片。

## 模組說明

### `main.py`

建立 PyObjC 視窗、按鈕、狀態文字與設定視窗。啟動時會開兩個背景執行緒：

- `mouse_engine.random_walk`
- `user_watch.start_watch`

### `mouse_engine.py`

負責主要自動化流程：

- 讀取螢幕尺寸。
- 隨機選擇滑鼠目標點。
- 用貝茲曲線產生較自然的移動路徑。
- 隨機滾動頁面。
- 按設定機率呼叫 Chrome 分頁切換。
- 在使用者輸入後暫停。

### `user_watch.py`

透過 Quartz Event Tap 監聽滑鼠移動。偵測到使用者移動滑鼠時，會呼叫 `mouse_engine.pause_for_30s()`，實際暫停秒數由 `settings.json` 的 `think_time` 決定。

### `chrome_control.py`

使用 `osascript` 執行 AppleScript，隨機切換 Google Chrome 前景視窗中的分頁。若 Chrome 沒有視窗或只有一個分頁，則不做任何事。

### `settings.py`

提供設定讀寫 API：

- `load()`
- `save()`
- `get(key)`
- `set(key, value)`

## 常見問題

### 滑鼠沒有移動

請確認執行程式已取得 macOS「輔助使用」權限。若是從終端機執行，授權對象通常是終端機或 IDE，而不是 Python 本身。

### Chrome 分頁沒有切換

請確認：

- Google Chrome 已開啟。
- 前景 Chrome 視窗至少有兩個分頁。
- macOS 已允許此程式控制 Google Chrome。

### 設定儲存後沒有變化

設定視窗按下儲存後會寫入 `settings.json`。如果是打包後的 `.app`，請確認 `.app` 所在位置或執行檔旁邊可寫入設定檔。

### 使用者移動滑鼠後工具停住

這是預期行為。`user_watch.py` 會在使用者移動滑鼠時暫停自動化，避免工具和使用者搶控制權。暫停時間由 `think_time` 控制。

## 開發備註

- `build/` 與 `dist/` 是打包輸出，通常不需要手動修改。
- `package-lock.json` 目前沒有實際 Node.js 依賴，主程式是 Python 專案。
- UI 使用 PyObjC/Cocoa 原生元件，背景圖片透過 `dopamine_ui.NeonBackground` 載入。
- 若修改圖片檔名，需同步更新 `dopamine_ui.py`、`main.py` 與 PyInstaller `.spec` 的 `datas`。

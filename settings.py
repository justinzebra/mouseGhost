import json
import os
import sys

# ===============================
# 正確決定設定檔位置
# ===============================
if hasattr(sys, "_MEIPASS"):
    # PyInstaller 模式（.app）
    BASE = os.path.dirname(sys.executable)
else:
    # 原始碼模式
    BASE = os.path.dirname(os.path.abspath(__file__))

FILE = os.path.join(BASE, "settings.json")

# ===============================
# 預設值
# ===============================
DEFAULT = {
    "scroll_probability": 0.9,
    "scroll_min_interval": 4,
    "tab_probability": 0.4,
    "tab_min_interval": 15,
    "think_time": 30
}

_settings = DEFAULT.copy()

# ===============================
# 讀取
# ===============================
def load():
    global _settings
    if os.path.exists(FILE):
        try:
            with open(FILE, "r") as f:
                _settings = json.load(f)
        except:
            _settings = DEFAULT.copy()
    else:
        _settings = DEFAULT.copy()
    return _settings

# ===============================
# 儲存
# ===============================
def save():
    with open(FILE, "w") as f:
        json.dump(_settings, f, indent=2)

# ===============================
# API
# ===============================
def get(key):
    return _settings.get(key, DEFAULT.get(key))

def set(key, value):
    _settings[key] = value
    save()

# ===============================
# 啟動時自動載入
# ===============================
load()

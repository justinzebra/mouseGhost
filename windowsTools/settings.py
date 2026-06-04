import json
import os
import sys


DEFAULT = {
    "scroll_probability": 0.9,
    "scroll_min_interval": 4,
    "tab_probability": 0.4,
    "tab_min_interval": 15,
    "think_time": 30,
}


def _base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


FILE = os.path.join(_base_dir(), "settings.json")
_settings = DEFAULT.copy()


def load():
    global _settings
    if not os.path.exists(FILE):
        _settings = DEFAULT.copy()
        save()
        return _settings

    try:
        with open(FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        _settings = {**DEFAULT, **loaded}
    except (OSError, json.JSONDecodeError):
        _settings = DEFAULT.copy()
    return _settings


def save():
    os.makedirs(os.path.dirname(FILE), exist_ok=True)
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(_settings, f, indent=2)


def get(key):
    return _settings.get(key, DEFAULT.get(key))


def set(key, value):
    _settings[key] = value
    save()


load()

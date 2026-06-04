import ctypes
import random
import time
from ctypes import wintypes


user32 = ctypes.WinDLL("user32", use_last_error=True)

EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_TAB = 0x09
KEYEVENTF_KEYUP = 0x0002


def _window_text(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def _class_name(hwnd):
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buffer, 256)
    return buffer.value


def _find_chrome_window():
    found = []

    @EnumWindowsProc
    def callback(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        title = _window_text(hwnd)
        class_name = _class_name(hwnd)
        if class_name == "Chrome_WidgetWin_1" and "Chrome" in title:
            found.append(hwnd)
            return False
        return True

    user32.EnumWindows(callback, 0)
    return found[0] if found else None


def _tap_key(vk):
    user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.03)
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def switch_chrome_tab():
    hwnd = _find_chrome_window()
    if not hwnd:
        return

    user32.ShowWindow(hwnd, 5)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.08)

    use_shift = random.choice([False, True])
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    if use_shift:
        user32.keybd_event(VK_SHIFT, 0, 0, 0)

    _tap_key(VK_TAB)

    if use_shift:
        user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

import ctypes
import random
import time
from ctypes import wintypes

import chrome_control
import settings


user32 = ctypes.WinDLL("user32", use_last_error=True)

SM_CXSCREEN = 0
SM_CYSCREEN = 1
MOUSEEVENTF_WHEEL = 0x0800
WHEEL_DELTA = 120

W = user32.GetSystemMetrics(SM_CXSCREEN)
H = user32.GetSystemMetrics(SM_CYSCREEN)

active = False
status = "idle"
remaining = 0
paused_until = 0

last_scroll = 0
last_tab_switch = 0
programmatic_until = 0

SAFE_MARGIN = 60


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


def mark_programmatic(seconds=0.25):
    global programmatic_until
    programmatic_until = max(programmatic_until, time.time() + seconds)


def get_mouse_pos():
    point = POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y


def set_mouse(x, y):
    mark_programmatic()
    user32.SetCursorPos(int(x), int(y))


def scroll(amount):
    mark_programmatic(0.35)
    user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, int(amount) * WHEEL_DELTA, 0)


def ease_in_out(t):
    return t * t * (3 - 2 * t)


def bezier(p0, p1, p2, p3, t):
    return (
        (1 - t) ** 3 * p0
        + 3 * (1 - t) ** 2 * t * p1
        + 3 * (1 - t) * t ** 2 * p2
        + t ** 3 * p3
    )


def human_move(x1, y1, x2, y2):
    duration = random.uniform(0.6, 1.6)
    steps = max(1, int(duration * 90))

    cx1 = x1 + random.uniform(-200, 200)
    cy1 = y1 + random.uniform(-200, 200)
    cx2 = x2 + random.uniform(-200, 200)
    cy2 = y2 + random.uniform(-200, 200)

    mark_programmatic(duration + 0.4)
    for i in range(steps):
        if not active or time.time() < paused_until:
            return

        t = i / steps
        t2 = ease_in_out(t)

        x = bezier(x1, cx1, cx2, x2, t2) + random.uniform(-1.5, 1.5)
        y = bezier(y1, cy1, cy2, y2, t2) + random.uniform(-1.5, 1.5)

        set_mouse(x, y)
        time.sleep(1 / 90)


def pick_target():
    return (
        random.randint(SAFE_MARGIN, max(SAFE_MARGIN, W - SAFE_MARGIN)),
        random.randint(SAFE_MARGIN, max(SAFE_MARGIN, H - SAFE_MARGIN)),
    )


def pause_for_30s():
    global paused_until, status
    if not active:
        return
    paused_until = time.time() + settings.get("think_time")
    status = "paused"


def interruptible_sleep(seconds):
    global remaining
    end = time.time() + seconds
    while time.time() < end:
        if not active or time.time() < paused_until:
            return
        remaining = int(end - time.time())
        time.sleep(0.2)


def burst_scroll():
    direction = random.choice([-1, 1])
    bursts = random.randint(2, 4)
    for _ in range(bursts):
        if not active:
            return
        amount = random.randint(3, 14)
        scroll(direction * amount)
        time.sleep(random.uniform(0.15, 0.5))


def random_walk():
    global status, remaining, last_scroll, last_tab_switch

    while True:
        if not active:
            status = "idle"
            remaining = 0
            time.sleep(0.2)
            continue

        if time.time() < paused_until:
            status = "paused"
            remaining = int(paused_until - time.time())
            time.sleep(0.2)
            continue

        status = "running"
        remaining = 0
        now = time.time()

        if (
            random.random() < settings.get("scroll_probability")
            and now - last_scroll > settings.get("scroll_min_interval")
        ):
            burst_scroll()
            last_scroll = now

        if (
            random.random() < settings.get("tab_probability")
            and now - last_tab_switch > settings.get("tab_min_interval")
        ):
            chrome_control.switch_chrome_tab()
            last_tab_switch = now

        x1, y1 = get_mouse_pos()
        x2, y2 = pick_target()
        human_move(x1, y1, x2, y2)
        interruptible_sleep(settings.get("think_time"))

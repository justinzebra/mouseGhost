import random
import time
from Quartz import *
import chrome_control
import settings

# ===== 螢幕 =====
screen = CGDisplayBounds(CGMainDisplayID())
W = int(screen.size.width)
H = int(screen.size.height)

# ===== 狀態 =====
active = False
status = "idle"
remaining = 0
paused_until = 0

last_scroll = 0
last_tab_switch = 0

SAFE_MARGIN = 60

# ==========================
# Low-level mouse
# ==========================

def get_mouse_pos():
    e = CGEventCreate(None)
    p = CGEventGetLocation(e)
    return p.x, p.y

def set_mouse(x, y):
    evt = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (x, y), 0)
    CGEventPost(kCGHIDEventTap, evt)

def scroll(amount):
    evt = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitLine, 1, int(amount))
    CGEventPost(kCGHIDEventTap, evt)

# ==========================
# Human motion
# ==========================

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def bezier(p0, p1, p2, p3, t):
    return (
        (1 - t) ** 3 * p0 +
        3 * (1 - t) ** 2 * t * p1 +
        3 * (1 - t) * t ** 2 * p2 +
        t ** 3 * p3
    )

def human_move(x1, y1, x2, y2):
    duration = random.uniform(0.6, 1.6)
    steps = int(duration * 90)

    cx1 = x1 + random.uniform(-200, 200)
    cy1 = y1 + random.uniform(-200, 200)
    cx2 = x2 + random.uniform(-200, 200)
    cy2 = y2 + random.uniform(-200, 200)

    for i in range(steps):
        t = i / steps
        t2 = ease_in_out(t)

        x = bezier(x1, cx1, cx2, x2, t2)
        y = bezier(y1, cy1, cy2, y2, t2)

        x += random.uniform(-1.5, 1.5)
        y += random.uniform(-1.5, 1.5)

        set_mouse(x, y)
        time.sleep(1 / 90)

# ==========================
# Target
# ==========================

def pick_target():
    return (
        random.randint(SAFE_MARGIN, W - SAFE_MARGIN),
        random.randint(SAFE_MARGIN, H - SAFE_MARGIN),
    )

# ==========================
# Pause
# ==========================

def pause_for_30s():
    global paused_until, status
    paused_until = time.time() + settings.get("think_time")
    status = "paused"

# ==========================
# 可中斷 sleep
# ==========================

def interruptible_sleep(seconds):
    global remaining
    end = time.time() + seconds
    while time.time() < end:
        if time.time() < paused_until:
            return
        remaining = int(end - time.time())
        time.sleep(0.2)

# ==========================
# Burst scroll
# ==========================

def burst_scroll():
    direction = random.choice([-1, 1])
    bursts = random.randint(2, 4)
    for _ in range(bursts):
        amount = random.randint(3, 14)
        scroll(direction * amount)
        time.sleep(random.uniform(0.15, 0.5))

# ==========================
# Main loop
# ==========================

def random_walk():
    global status, remaining, last_scroll, last_tab_switch

    while True:
        if not active:
            status = "idle"
            time.sleep(0.2)
            continue

        if time.time() < paused_until:
            status = "paused"
            remaining = int(paused_until - time.time())
            time.sleep(0.2)
            continue

        status = "running"
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

        # 🔥 用可中斷 sleep
        interruptible_sleep(settings.get("think_time"))

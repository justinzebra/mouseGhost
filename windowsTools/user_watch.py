import math
import threading
import time

import mouse_engine


_stop = threading.Event()
_thread = None


def _watch_loop():
    last = mouse_engine.get_mouse_pos()
    while not _stop.is_set():
        time.sleep(0.08)
        current = mouse_engine.get_mouse_pos()
        distance = math.hypot(current[0] - last[0], current[1] - last[1])

        if (
            mouse_engine.active
            and distance > 4
            and time.time() > mouse_engine.programmatic_until
        ):
            mouse_engine.pause_for_30s()

        last = current


def start_watch():
    global _thread
    if _thread and _thread.is_alive():
        return
    _stop.clear()
    _thread = threading.Thread(target=_watch_loop, daemon=True)
    _thread.start()


def stop_watch():
    _stop.set()

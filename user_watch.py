from Quartz import *
import mouse_engine

tap = None
runLoopSource = None
runLoop = None

def callback(proxy, type, event, refcon):
    if type == kCGEventMouseMoved:
        mouse_engine.pause_for_30s()
    return event

def start_watch():
    global tap, runLoopSource, runLoop

    tap = CGEventTapCreate(
        kCGSessionEventTap,
        kCGHeadInsertEventTap,
        0,
        CGEventMaskBit(kCGEventMouseMoved),
        callback,
        None
    )

    runLoop = CFRunLoopGetCurrent()
    runLoopSource = CFMachPortCreateRunLoopSource(None, tap, 0)
    CFRunLoopAddSource(runLoop, runLoopSource, kCFRunLoopCommonModes)
    CGEventTapEnable(tap, True)
    CFRunLoopRun()

def stop_watch():
    global tap, runLoopSource, runLoop
    if tap:
        CGEventTapEnable(tap, False)
    if runLoopSource and runLoop:
        CFRunLoopRemoveSource(runLoop, runLoopSource, kCFRunLoopCommonModes)
    tap = None
    runLoopSource = None
    runLoop = None

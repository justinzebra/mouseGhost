import objc
import threading
from Cocoa import *

import mouse_engine
import user_watch
import settings

from dopamine_ui import NeonBackground, make_glow_label, make_neon_button


# ===============================
# 主視窗 Controller
# ===============================

class App(NSObject):
    statusLabel = None
    bg = None
    settingsWindow = None

    @objc.IBAction
    def start_(self, sender):
        mouse_engine.active = True
        self.statusLabel.setStringValue_("🟢 偷懶中，我是一頭開心的小豬 🐷")
        self.bg.setBackground_("主題1.png")

    @objc.IBAction
    def stop_(self, sender):
        mouse_engine.active = False
        self.statusLabel.setStringValue_("🔴 停止偷懶，我為什麼要工作嗚嗚嗚 😭")
        self.bg.setBackground_("主題2.png")

    @objc.IBAction
    def openSettings_(self, sender):
        if not self.settingsWindow:
            self.settingsWindow = SettingsWindow.alloc().init()
        self.settingsWindow.show()

    @objc.IBAction
    def close_(self, sender):
        try:
            user_watch.stop_watch()   # 🔥 釋放 EventTap，防止 macOS 被拖死
        except:
            pass
        NSApplication.sharedApplication().terminate_(None)


# ===============================
# 設定視窗（Slider 控制台）
# ===============================

class SettingsWindow(NSObject):

    def init(self):
        self = objc.super(SettingsWindow, self).init()
        if not self:
            return None

        self.win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            ((0, 0), (480, 360)),
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
            NSBackingStoreBuffered,
            False
        )
        self.win.setTitle_("MouseGhost 控制台")

        self.view = NSView.alloc().initWithFrame_(((0,0),(480,360)))
        self.win.setContentView_(self.view)

        self.sliders = {}
        self.labels = {}
        self.savedLabel = None

        y = 300

        def add_slider(title, key, minv, maxv, isFloat=True):
            nonlocal y

            lbl = NSTextField.alloc().initWithFrame_(((20,y),(200,22)))
            lbl.setStringValue_(title)
            lbl.setEditable_(False)
            lbl.setBordered_(False)
            lbl.setDrawsBackground_(False)

            slider = NSSlider.alloc().initWithFrame_(((200,y),(200,22)))
            slider.setMinValue_(minv)
            slider.setMaxValue_(maxv)
            slider.setDoubleValue_(settings.get(key))
            slider.setTarget_(self)
            slider.setAction_("onSlide:")

            val = NSTextField.alloc().initWithFrame_(((420,y),(50,22)))
            val.setEditable_(False)
            val.setBordered_(False)
            val.setDrawsBackground_(False)

            if isFloat:
                val.setStringValue_(f"{settings.get(key):.2f}")
            else:
                val.setStringValue_(str(int(settings.get(key))))

            self.sliders[slider] = (key, isFloat)
            self.labels[slider] = val

            self.view.addSubview_(lbl)
            self.view.addSubview_(slider)
            self.view.addSubview_(val)

            y -= 50

        add_slider("滾動機率", "scroll_probability", 0, 1)
        add_slider("滾動間隔（秒）", "scroll_min_interval", 1, 20, False)
        add_slider("切分頁機率", "tab_probability", 0, 1)
        add_slider("切分頁間隔（秒）", "tab_min_interval", 5, 60, False)
        add_slider("思考時間（秒）", "think_time", 1, 1000, False)

        # 儲存
        btnSave = NSButton.alloc().initWithFrame_(((80, 20), (120, 40)))
        btnSave.setTitle_("💾 儲存")
        btnSave.setTarget_(self)
        btnSave.setAction_("save:")
        self.view.addSubview_(btnSave)

        # 返回
        btnBack = NSButton.alloc().initWithFrame_(((280, 20), (120, 40)))
        btnBack.setTitle_("⬅ 返回")
        btnBack.setTarget_(self)
        btnBack.setAction_("back:")
        self.view.addSubview_(btnBack)

        return self

    def show(self):
        self.win.center()
        self.win.makeKeyAndOrderFront_(None)

    @objc.IBAction
    def onSlide_(self, slider):
        key, isFloat = self.sliders[slider]
        val = slider.doubleValue()
        if isFloat:
            self.labels[slider].setStringValue_(f"{val:.2f}")
        else:
            self.labels[slider].setStringValue_(str(int(val)))

    @objc.IBAction
    def save_(self, sender):
        for slider, (key, isFloat) in self.sliders.items():
            val = slider.doubleValue()
            if not isFloat:
                val = int(val)
            settings.set(key, val)

        self.showSavedLabel()

    @objc.IBAction
    def back_(self, sender):
        self.win.orderOut_(None)

    # ===== 視窗內 Label 提示（PyInstaller 穩定）=====
    def showSavedLabel(self):
        if self.savedLabel:
            self.savedLabel.removeFromSuperview()

        self.savedLabel = NSTextField.alloc().initWithFrame_(((120, 140), (240, 30)))
        self.savedLabel.setStringValue_("✔ 設定已儲存")
        self.savedLabel.setAlignment_(1)
        self.savedLabel.setEditable_(False)
        self.savedLabel.setBordered_(False)
        self.savedLabel.setDrawsBackground_(True)
        self.savedLabel.setBackgroundColor_(NSColor.colorWithCalibratedWhite_alpha_(0, 0.75))
        self.savedLabel.setTextColor_(NSColor.whiteColor())

        self.view.addSubview_(self.savedLabel)

        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            2.0, self.savedLabel, "removeFromSuperview", None, False
        )


# ===============================
# App 入口
# ===============================

def main():
    threading.Thread(target=mouse_engine.random_walk, daemon=True).start()
    threading.Thread(target=user_watch.start_watch, daemon=True).start()

    app = NSApplication.sharedApplication()
    controller = App.alloc().init()

    window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        ((0, 0), (420, 260)),
        NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
        NSBackingStoreBuffered,
        False
    )
    window.setTitle_("Mouse Ghost 👻")
    window.setMinSize_((420, 260))
    window.setMaxSize_((420, 260))

    bg = NeonBackground.alloc().initWithFrame_(((0, 0), (420, 260)))
    window.setContentView_(bg)
    controller.bg = bg

    status = make_glow_label(((40, 190), (340, 40)), "🔴 停止偷懶模式", 18)
    controller.statusLabel = status

    btnStart = make_neon_button(((110, 120), (200, 45)), "▶ 開始偷懶", True)
    btnStart.setTarget_(controller)
    btnStart.setAction_("start:")

    btnStop = make_neon_button(((110, 65), (200, 45)), "⏹ 停止偷懶", False)
    btnStop.setTarget_(controller)
    btnStop.setAction_("stop:")

    btnSettings = make_neon_button(((20, 20), (100, 30)), "⚙ 設定", False)
    btnSettings.setTarget_(controller)
    btnSettings.setAction_("openSettings:")

    btnClose = make_neon_button(((300, 20), (100, 30)), "✖ 關閉", False)
    btnClose.setTarget_(controller)
    btnClose.setAction_("close:")

    bg.addSubview_(status)
    bg.addSubview_(btnStart)
    bg.addSubview_(btnStop)
    bg.addSubview_(btnSettings)
    bg.addSubview_(btnClose)

    window.center()
    window.makeKeyAndOrderFront_(None)
    app.run()


if __name__ == "__main__":
    main()

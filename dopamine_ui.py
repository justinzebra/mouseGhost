import objc
import os
import sys
from Cocoa import *

MAGENTA = NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.23, 0.95, 1.0)
CYAN    = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.0, 0.95, 0.83, 1.0)
YELLOW  = NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.9, 0.0, 1.0)

class NeonBackground(NSView):

    def initWithFrame_(self, frame):
        self = objc.super(NeonBackground, self).initWithFrame_(frame)
        if self is None:
            return None

        # 🔥 PyInstaller & 開發模式都能抓到圖片
        if hasattr(sys, "_MEIPASS"):
            self.base = sys._MEIPASS
        else:
            self.base = os.path.dirname(os.path.abspath(__file__))

        self.bg = NSImageView.alloc().initWithFrame_(self.bounds())
        self.bg.setImageScaling_(NSImageScaleAxesIndependently)
        self.addSubview_(self.bg)

        self.overlay = NSView.alloc().initWithFrame_(self.bounds())
        self.overlay.setWantsLayer_(True)
        self.overlay.layer().setBackgroundColor_(NSColor.colorWithCalibratedWhite_alpha_(0, 0.55).CGColor())
        self.addSubview_(self.overlay)

        self.setBackground_("主題.png")
        return self

    def setBackground_(self, filename):
        path = os.path.join(self.base, filename)
        if os.path.exists(path):
            img = NSImage.alloc().initWithContentsOfFile_(path)
            self.bg.setImage_(img)
            print("🖼 背景:", filename)
        else:
            print("❌ 找不到:", path)

    def layout(self):
        objc.super(NeonBackground, self).layout()
        self.bg.setFrame_(self.bounds())
        self.overlay.setFrame_(self.bounds())


def make_glow_label(frame, text, size=16):
    lbl = NSTextField.alloc().initWithFrame_(frame)
    lbl.setStringValue_(text)
    lbl.setBezeled_(False)
    lbl.setDrawsBackground_(False)
    lbl.setEditable_(False)
    lbl.setSelectable_(False)
    lbl.setAlignment_(1)
    lbl.setFont_(NSFont.systemFontOfSize_weight_(size, NSFontWeightBlack))
    lbl.setTextColor_(NSColor.whiteColor())

    shadow = NSShadow.alloc().init()
    shadow.setShadowColor_(MAGENTA)
    shadow.setShadowBlurRadius_(14)
    shadow.setShadowOffset_((0, 0))
    lbl.setShadow_(shadow)
    return lbl


def make_neon_button(frame, title, primary=True):
    btn = NSButton.alloc().initWithFrame_(frame)
    btn.setTitle_(title.upper())
    btn.setBordered_(False)
    btn.setFont_(NSFont.systemFontOfSize_weight_(15, NSFontWeightBlack))
    btn.setWantsLayer_(True)
    btn.layer().setCornerRadius_(frame[1][1] / 2)
    btn.layer().setBorderWidth_(4)

    if primary:
        btn.layer().setBackgroundColor_(MAGENTA.CGColor())
        btn.layer().setBorderColor_(YELLOW.CGColor())
        btn.setContentTintColor_(NSColor.blackColor())
    else:
        btn.layer().setBackgroundColor_(CYAN.CGColor())
        btn.layer().setBorderColor_(MAGENTA.CGColor())
        btn.setContentTintColor_(NSColor.blackColor())

    btn.layer().setShadowColor_(MAGENTA.CGColor())
    btn.layer().setShadowOpacity_(0.9)
    btn.layer().setShadowRadius_(20)
    btn.layer().setShadowOffset_((0, 0))
    return btn

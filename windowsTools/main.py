import threading
import tkinter as tk
from tkinter import ttk

import mouse_engine
import settings
import user_watch


COLORS = {
    "bg": "#f5f7fb",
    "panel": "#ffffff",
    "panel_alt": "#eef3f8",
    "line": "#d9e2ec",
    "text": "#1f2937",
    "muted": "#64748b",
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "success": "#0f766e",
    "danger": "#b91c1c",
    "warning": "#b45309",
}

FONT = "Segoe UI"


class SettingsWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("AutoNotes Settings")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])
        self.transient(master)

        self.vars = {}
        self.value_labels = {}

        body = ttk.Frame(self, padding=22, style="Card.TFrame")
        body.grid(row=0, column=0, sticky="nsew")

        rows = [
            ("Auto format level", "scroll_probability", 0, 1, True),
            ("Review interval", "scroll_min_interval", 1, 20, False),
            ("Topic scan level", "tab_probability", 0, 1, True),
            ("Sync interval", "tab_min_interval", 5, 60, False),
            ("Draft delay", "think_time", 1, 1000, False),
        ]

        ttk.Label(body, text="Notebook Preferences", style="Title.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 14)
        )

        for row, (label, key, minv, maxv, is_float) in enumerate(rows):
            grid_row = row + 1
            ttk.Label(body, text=label, width=18, style="Body.TLabel").grid(
                row=grid_row, column=0, sticky="w", pady=9
            )
            var = tk.DoubleVar(value=settings.get(key))
            scale = ttk.Scale(
                body,
                from_=minv,
                to=maxv,
                variable=var,
                command=lambda _, k=key: self._update_value(k),
                length=240,
            )
            scale.grid(row=grid_row, column=1, sticky="ew", padx=12)
            value = ttk.Label(body, width=8, style="Value.TLabel")
            value.grid(row=grid_row, column=2, sticky="e")
            self.vars[key] = (var, is_float)
            self.value_labels[key] = value
            self._update_value(key)

        buttons = ttk.Frame(body)
        buttons.grid(row=len(rows) + 1, column=0, columnspan=3, pady=(20, 0), sticky="ew")
        ttk.Button(buttons, text="儲存設定", style="Primary.TButton", command=self.save).pack(
            side="left", expand=True, fill="x", padx=(0, 8)
        )
        ttk.Button(buttons, text="返回", command=self.withdraw).pack(
            side="left", expand=True, fill="x", padx=(8, 0)
        )

    def _update_value(self, key):
        var, is_float = self.vars[key]
        value = var.get()
        text = f"{value:.2f}" if is_float else str(int(value))
        self.value_labels[key].configure(text=text)

    def save(self):
        for key, (var, is_float) in self.vars.items():
            value = var.get()
            settings.set(key, value if is_float else int(value))
        self.withdraw()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoNotes")
        self.geometry("860x560")
        self.minsize(860, 560)
        self.configure(bg=COLORS["bg"])
        self.settings_window = None
        self.notice_var = tk.StringVar(value="Ready")

        self._configure_style()
        self._build_layout()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(200, self.refresh_status)

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Root.TFrame", background=COLORS["bg"])
        style.configure("Card.TFrame", background=COLORS["panel"], relief="flat")
        style.configure("Sidebar.TFrame", background=COLORS["panel_alt"])
        style.configure("Toolbar.TFrame", background=COLORS["panel"])
        style.configure("TButton", font=(FONT, 10), padding=(12, 7), borderwidth=0)
        style.map("TButton", background=[("active", COLORS["panel_alt"])])
        style.configure(
            "Primary.TButton",
            font=(FONT, 10, "bold"),
            foreground="#ffffff",
            background=COLORS["primary"],
            padding=(14, 8),
        )
        style.map("Primary.TButton", background=[("active", COLORS["primary_hover"])])
        style.configure(
            "Danger.TButton",
            font=(FONT, 10, "bold"),
            foreground="#ffffff",
            background=COLORS["danger"],
            padding=(14, 8),
        )
        style.configure("Title.TLabel", background=COLORS["panel"], foreground=COLORS["text"], font=(FONT, 16, "bold"))
        style.configure("Body.TLabel", background=COLORS["panel"], foreground=COLORS["text"], font=(FONT, 10))
        style.configure("Muted.TLabel", background=COLORS["panel"], foreground=COLORS["muted"], font=(FONT, 9))
        style.configure("Value.TLabel", background=COLORS["panel"], foreground=COLORS["primary"], font=(FONT, 10, "bold"))
        style.configure("Sidebar.TLabel", background=COLORS["panel_alt"], foreground=COLORS["text"], font=(FONT, 10))
        style.configure("SidebarTitle.TLabel", background=COLORS["panel_alt"], foreground=COLORS["text"], font=(FONT, 15, "bold"))

    def _build_layout(self):
        shell = ttk.Frame(self, padding=18, style="Root.TFrame")
        shell.pack(fill="both", expand=True)

        header = ttk.Frame(shell, style="Root.TFrame")
        header.pack(fill="x", pady=(0, 12))

        title_area = ttk.Frame(header, style="Root.TFrame")
        title_area.pack(side="left")
        tk.Label(
            title_area,
            text="AutoNotes",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=(FONT, 24, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_area,
            text="Meeting notes, summaries, and workspace drafts",
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=(FONT, 10),
        ).pack(anchor="w", pady=(2, 0))

        status_card = tk.Frame(header, bg=COLORS["panel"], highlightbackground=COLORS["line"], highlightthickness=1)
        status_card.pack(side="right", ipadx=18, ipady=10)
        tk.Label(status_card, text="Session", bg=COLORS["panel"], fg=COLORS["muted"], font=(FONT, 9)).pack(anchor="e")
        self.status_label = tk.Label(
            status_card,
            text="待命中",
            font=(FONT, 13, "bold"),
            fg=COLORS["muted"],
            bg=COLORS["panel"],
        )
        self.status_label.pack(anchor="e")

        toolbar = ttk.Frame(shell, padding=(12, 10), style="Toolbar.TFrame")
        toolbar.pack(fill="x", pady=(0, 12))

        ttk.Button(toolbar, text="開始筆記", style="Primary.TButton", command=self.start).pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="停止筆記", style="Danger.TButton", command=self.stop).pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="新增筆記", command=self.noop).pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="匯入錄音", command=self.noop).pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="整理重點", command=self.noop).pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="匯出摘要", command=self.noop).pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="設定", command=self.open_settings).pack(side="right", padx=(8, 0))

        content = ttk.Frame(shell, style="Root.TFrame")
        content.pack(fill="both", expand=True)

        sidebar = ttk.Frame(content, width=220, padding=14, style="Sidebar.TFrame")
        sidebar.pack(side="left", fill="y", padx=(0, 12))
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text="筆記資料夾", style="SidebarTitle.TLabel").pack(anchor="w", pady=(0, 12))

        for item in ["今日會議", "產品想法", "客戶訪談", "待整理草稿", "封存筆記"]:
            row = tk.Label(
                sidebar,
                text=item,
                anchor="w",
                bg=COLORS["panel_alt"],
                fg=COLORS["text"],
                font=(FONT, 10),
                padx=10,
                pady=8,
            )
            row.pack(fill="x", pady=2)

        ttk.Button(sidebar, text="同步雲端", command=self.noop).pack(fill="x", side="bottom", pady=(8, 0))
        ttk.Button(sidebar, text="搜尋筆記", command=self.noop).pack(fill="x", side="bottom", pady=(8, 0))

        editor = tk.Frame(content, bg=COLORS["panel"], highlightbackground=COLORS["line"], highlightthickness=1)
        editor.pack(side="left", fill="both", expand=True)

        editor_header = tk.Frame(editor, bg=COLORS["panel"])
        editor_header.pack(fill="x", padx=18, pady=(16, 10))
        tk.Label(
            editor_header,
            text="Untitled Meeting Notes",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=(FONT, 18, "bold"),
        ).pack(side="left")
        tk.Label(
            editor_header,
            textvariable=self.notice_var,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=(FONT, 9),
        ).pack(side="right")

        self.editor_text = tk.Text(
            editor,
            wrap="word",
            height=12,
            relief="flat",
            bg="#fbfdff",
            fg=COLORS["text"],
            insertbackground=COLORS["primary"],
            font=(FONT, 11),
            padx=16,
            pady=14,
        )
        self.editor_text.pack(fill="both", expand=True, padx=18, pady=(0, 14))
        self.editor_text.insert(
            "1.0",
            "會議摘要\n\n- 自動產生的筆記草稿會出現在這裡。\n- 可使用上方工具列整理重點、匯出摘要或同步資料。\n\n",
        )

        footer = ttk.Frame(shell, style="Root.TFrame")
        footer.pack(fill="x", pady=(12, 0))
        tk.Label(
            footer,
            text="Local notebook workspace",
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=(FONT, 9),
        ).pack(side="left")
        ttk.Button(footer, text="關閉應用程式", command=self.close).pack(side="right")

    def noop(self):
        return None

    def start(self):
        mouse_engine.active = True
        mouse_engine.status = "running"
        self.notice_var.set("Recording notes")

    def stop(self):
        mouse_engine.active = False
        mouse_engine.status = "idle"
        self.notice_var.set("Stopped")

    def open_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
        self.settings_window.deiconify()
        self.settings_window.lift()

    def close(self):
        user_watch.stop_watch()
        self.destroy()

    def refresh_status(self):
        status = mouse_engine.status
        if status == "running":
            text = "筆記中"
            color = COLORS["success"]
        elif status == "paused":
            text = f"整理中 {mouse_engine.remaining}s"
            color = COLORS["warning"]
        else:
            text = "待命中"
            color = COLORS["muted"]

        self.status_label.configure(text=text, fg=color)
        self.after(200, self.refresh_status)


def main():
    threading.Thread(target=mouse_engine.random_walk, daemon=True).start()
    user_watch.start_watch()
    App().mainloop()


if __name__ == "__main__":
    main()

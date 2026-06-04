import threading
import tkinter as tk
from tkinter import ttk

import mouse_engine
import settings
import user_watch


BG_IDLE = "#101820"
BG_ACTIVE = "#123524"
BG_PAUSED = "#2b263d"
FG = "#f4f7fb"
ACCENT = "#6ee7b7"
WARN = "#fbbf24"


class SettingsWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("MouseGhost Settings")
        self.resizable(False, False)
        self.configure(bg=BG_IDLE)
        self.transient(master)

        self.vars = {}
        self.value_labels = {}

        body = ttk.Frame(self, padding=20)
        body.grid(row=0, column=0, sticky="nsew")

        rows = [
            ("Scroll chance", "scroll_probability", 0, 1, True),
            ("Scroll interval", "scroll_min_interval", 1, 20, False),
            ("Tab chance", "tab_probability", 0, 1, True),
            ("Tab interval", "tab_min_interval", 5, 60, False),
            ("Think time", "think_time", 1, 1000, False),
        ]

        for row, (label, key, minv, maxv, is_float) in enumerate(rows):
            ttk.Label(body, text=label, width=16).grid(row=row, column=0, sticky="w", pady=8)
            var = tk.DoubleVar(value=settings.get(key))
            scale = ttk.Scale(
                body,
                from_=minv,
                to=maxv,
                variable=var,
                command=lambda _, k=key: self._update_value(k),
                length=240,
            )
            scale.grid(row=row, column=1, sticky="ew", padx=10)
            value = ttk.Label(body, width=8)
            value.grid(row=row, column=2, sticky="e")
            self.vars[key] = (var, is_float)
            self.value_labels[key] = value
            self._update_value(key)

        buttons = ttk.Frame(body)
        buttons.grid(row=len(rows), column=0, columnspan=3, pady=(18, 0), sticky="ew")
        ttk.Button(buttons, text="Save", command=self.save).pack(side="left", expand=True, fill="x", padx=(0, 8))
        ttk.Button(buttons, text="Back", command=self.withdraw).pack(side="left", expand=True, fill="x", padx=(8, 0))

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
        self.title("MouseGhost Windows")
        self.geometry("420x260")
        self.minsize(420, 260)
        self.maxsize(420, 260)
        self.configure(bg=BG_IDLE)
        self.settings_window = None

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11), padding=(12, 8))
        style.configure("TLabel", font=("Segoe UI", 10))

        self.status_label = tk.Label(
            self,
            text="Idle",
            font=("Segoe UI", 20, "bold"),
            fg=FG,
            bg=BG_IDLE,
        )
        self.status_label.pack(pady=(34, 22))

        self.start_button = ttk.Button(self, text="Start", command=self.start)
        self.start_button.pack(fill="x", padx=110, pady=4)

        self.stop_button = ttk.Button(self, text="Stop", command=self.stop)
        self.stop_button.pack(fill="x", padx=110, pady=4)

        footer = tk.Frame(self, bg=BG_IDLE)
        footer.pack(side="bottom", fill="x", padx=20, pady=18)
        ttk.Button(footer, text="Settings", command=self.open_settings).pack(side="left")
        ttk.Button(footer, text="Close", command=self.close).pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(200, self.refresh_status)

    def start(self):
        mouse_engine.active = True
        mouse_engine.status = "running"

    def stop(self):
        mouse_engine.active = False
        mouse_engine.status = "idle"

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
            bg = BG_ACTIVE
            text = "Running"
            color = ACCENT
        elif status == "paused":
            bg = BG_PAUSED
            text = f"Paused {mouse_engine.remaining}s"
            color = WARN
        else:
            bg = BG_IDLE
            text = "Idle"
            color = FG

        self.configure(bg=bg)
        self.status_label.configure(text=text, bg=bg, fg=color)
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=bg)
        self.after(200, self.refresh_status)


def main():
    threading.Thread(target=mouse_engine.random_walk, daemon=True).start()
    user_watch.start_watch()
    App().mainloop()


if __name__ == "__main__":
    main()

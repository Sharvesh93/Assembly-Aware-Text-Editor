import tkinter as tk
from tkinter import ttk
from typing import List, Dict


class ErrorPanel(tk.Frame):
    def __init__(self, parent, text_widget: tk.Text, font_ui=None, font_small=None, bg="#0a0a0a", fg="#ffffff", **kw):
        super().__init__(parent, bg=bg, **kw)
        self._text = text_widget
        self._font_ui = font_ui or ("Poppins", 10)
        self._font_small = font_small or ("Poppins", 9)
        self._bg = bg
        self._fg = fg
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=self._bg, pady=3)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="Diagnostics", bg=self._bg, fg=self._fg, font=self._font_ui).pack(side=tk.LEFT)
        self._summary = tk.Label(hdr, text="", bg=self._bg, fg=self._fg, font=self._font_small)
        self._summary.pack(side=tk.RIGHT, padx=10)
        st = ttk.Style()
        st.theme_use("default")
        st.configure(
            "Diag.Treeview",
            background=self._bg,
            foreground=self._fg,
            fieldbackground=self._bg,
            rowheight=22,
            font=self._font_small,
        )
        st.configure("Diag.Treeview.Heading", background=self._bg, foreground=self._fg, font=self._font_ui)
        st.map("Diag.Treeview", background=[("selected", "#333333")])
        frame = tk.Frame(self, bg=self._bg)
        frame.pack(fill=tk.BOTH, expand=True)
        cols = ("line", "sev", "msg")
        self._tree = ttk.Treeview(frame, columns=cols, show="headings", style="Diag.Treeview", selectmode="browse")
        self._tree.heading("line", text="Line")
        self._tree.heading("sev", text="Type")
        self._tree.heading("msg", text="Message")
        self._tree.column("line", width=55, anchor=tk.CENTER, stretch=False)
        self._tree.column("sev", width=90, anchor=tk.CENTER, stretch=False)
        self._tree.column("msg", width=800, anchor=tk.W)
        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self._tree.yview)
        hsb = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hsb.pack(fill=tk.X)
        self._tree.tag_configure("error", foreground="#ff6666")
        self._tree.tag_configure("warning", foreground="#ffff66")
        self._tree.tag_configure("info", foreground=self._fg)
        self._tree.bind("<Double-1>", self._jump)
        self._tree.bind("<Return>", self._jump)

    def show(self, errors: List[Dict]):
        for row in self._tree.get_children():
            self._tree.delete(row)
        if not errors:
            self._summary.config(text="No issues", fg=self._fg)
            return
        n_err = sum(1 for e in errors if e["severity"] == "error")
        n_warn = sum(1 for e in errors if e["severity"] == "warning")
        col = "#ff6666" if n_err else "#ffff66"
        parts = []
        if n_err:
            parts.append(f"{n_err} error(s)")
        if n_warn:
            parts.append(f"{n_warn} warning(s)")
        self._summary.config(text="  ".join(parts), fg=col)
        icons = {"error": "E", "warning": "W", "info": "i"}
        for e in errors:
            sev = e.get("severity", "info")
            icon = icons.get(sev, "")
            self._tree.insert("", tk.END, values=(e["line"], f"{icon} {sev}", e["message"]), tags=(sev,))

    def _jump(self, _=None):
        sel = self._tree.selection()
        if not sel:
            return
        try:
            line = int(self._tree.item(sel[0], "values")[0])
            self._text.mark_set(tk.INSERT, f"{line}.0")
            self._text.see(f"{line}.0")
            self._text.focus_set()
        except (ValueError, IndexError):
            pass

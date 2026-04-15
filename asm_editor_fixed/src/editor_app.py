import os
import tkinter as tk
from tkinter import filedialog, messagebox, font as tkfont
import configparser
from src.syntax_highlighter import SyntaxHighlighter
from src.linter import AsmLinter
from src.autosave import AutoSave
from src.emu_bridge import EmuBridge
from src.error_panel import ErrorPanel
from src.line_numbers import LineNumbers
from src.instruction_ref import InstructionTooltip
_TEMPLATE = """

org 100h

ret

"""

C = {
    "bg": "#1f2036",
    "fg": "#ffffff",
    "sel_bg": "#333333",
    "insert": "#ffffff",
    "err_ul": "#ff6666",
    "warn_ul": "#ffff66",
    "btn_bg": "#2b2f55",
    "btn_hover": "#276825",
    "btn_run_bg": "#145a78",
    "menu_bg": "#1f2036",
}

class AsmEditorApp(tk.Tk):
    LINT_DELAY_MS = 400

    def __init__(self):
        super().__init__()
        self._root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._cfg = configparser.ConfigParser()
        self._cfg.read(os.path.join(self._root_dir, "config.ini"))
        emu_path = self._cfg.get("emu8086", "path", fallback=r"A:\Emu\emu8086\emu8086.exe")
        font_size = self._cfg.getint("editor", "font_size", fallback=14)
        self._autosave_on_enter = self._cfg.get("editor", "autosave_on_enter", fallback="yes").strip().lower() in ("yes", "1", "true", "on")
        self._filepath = None
        self._modified = False
        self._lint_job = None
        self.title("MPMC Project – 8086 Assembly-Aware Text Editor")
        self.geometry("1600x900")
        self.minsize(860, 520)
        self.configure(bg=C["bg"])
        self._code_font = tkfont.Font(family="Poppins", size=font_size)
        self._small_font = tkfont.Font(family="Poppins", size=max(9, font_size - 4))
        self._ui_font = (self._code_font.actual("family"), max(9, font_size - 2))
        self._build_menu()
        self._build_ui()
        self._bind_keys()
        self._highlighter = SyntaxHighlighter(self._text)
        self._linter = AsmLinter()
        self._bridge = EmuBridge(emu_path)
        self._autosave = AutoSave(
            get_content=self._content,
            get_filepath=lambda: self._filepath,
            on_save=self._on_autosave_done,
        )
        self._autosave.start(self)
        self._tooltip = InstructionTooltip(self._text, C["bg"], C["fg"], self._small_font)
        self._new_file(silent=True)

    def _build_ui(self):
        tb = tk.Frame(self, bg=C["bg"], pady=4)
        tb.pack(fill=tk.X, side=tk.TOP)

        def btn(parent, text, cmd, run=False):
            b = tk.Button(
                parent,
                text=text,
                command=cmd,
                bg=C["btn_run_bg"] if run else C["btn_bg"],
                fg=C["fg"],
                activebackground=C["btn_hover"],
                activeforeground=C["fg"],
                relief=tk.FLAT,
                bd=0,
                padx=12,
                pady=4,
                cursor="hand2",
                font=self._ui_font,
            )
            return b

        btn(tb, "New", self._new_file).pack(side=tk.LEFT, padx=3)
        btn(tb, "Open", self._open_file).pack(side=tk.LEFT, padx=3)
        btn(tb, "Save", self._save_file).pack(side=tk.LEFT, padx=3)
        btn(tb, "Save As", self._save_as).pack(side=tk.LEFT, padx=3)
        tk.Frame(tb, bg=C["fg"], width=1).pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=2)
        btn(tb, "Open in EMU8086", self._run_emu, run=True).pack(side=tk.LEFT, padx=3)
        self._save_indicator = tk.Label(tb, text="", bg=C["bg"], fg=C["fg"], font=self._small_font)
        self._save_indicator.pack(side=tk.RIGHT, padx=10)
        pane = tk.PanedWindow(self, orient=tk.VERTICAL, bg=C["bg"], sashwidth=4, sashrelief=tk.FLAT)
        pane.pack(fill=tk.BOTH, expand=True)
        ed_frame = tk.Frame(pane, bg=C["bg"])
        pane.add(ed_frame, minsize=320)
        ed_row = tk.Frame(ed_frame, bg=C["bg"])
        ed_row.pack(fill=tk.BOTH, expand=True)
        self._text = tk.Text(
            ed_row,
            bg=C["bg"],
            fg=C["fg"],
            insertbackground=C["insert"],
            selectbackground=C["sel_bg"],
            selectforeground=C["fg"],
            font=self._code_font,
            undo=True,
            maxundo=500,
            wrap=tk.NONE,
            padx=10,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            tabs=("1c",),
            spacing1=1,
            spacing2=1,
        )
        self._line_nums = LineNumbers(ed_row, self._text, bg=C["bg"], fg=C["fg"], font=self._code_font)
        self._line_nums.pack(side=tk.LEFT, fill=tk.Y)
        y_sb = tk.Scrollbar(ed_row, orient=tk.VERTICAL, command=self._text.yview, bg=C["bg"], troughcolor=C["bg"], activebackground=C["btn_hover"])
        x_sb = tk.Scrollbar(ed_frame, orient=tk.HORIZONTAL, command=self._text.xview, bg=C["bg"], troughcolor=C["bg"], activebackground=C["btn_hover"])
        self._text.configure(yscrollcommand=y_sb.set, xscrollcommand=x_sb.set)
        y_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        x_sb.pack(fill=tk.X)
        self._err_panel = ErrorPanel(
            pane,
            self._text,
            font_ui=self._ui_font,
            font_small=self._small_font,
            bg=C["bg"],
            fg=C["fg"],
        )
        pane.add(self._err_panel, minsize=120)
        self._text.tag_configure("error_line", underline=True, foreground=C["err_ul"])
        self._text.tag_configure("warn_line", underline=True, foreground=C["warn_ul"])
        sb = tk.Frame(self, bg=C["bg"], height=26)
        sb.pack(fill=tk.X, side=tk.BOTTOM)
        sb.pack_propagate(False)
        self._st_file = tk.Label(sb, text="No file", bg=C["bg"], fg=C["fg"], font=self._ui_font, padx=10)
        self._st_file.pack(side=tk.LEFT)
        self._st_pos = tk.Label(sb, text="Ln 1  Col 1", bg=C["bg"], fg=C["fg"], font=self._ui_font, padx=10)
        self._st_pos.pack(side=tk.LEFT)
        self._st_err = tk.Label(sb, text="Errors: 0", bg=C["bg"], fg=C["fg"], font=self._ui_font, padx=10)
        self._st_err.pack(side=tk.RIGHT)
        tk.Label(sb, text="8086 ASM", bg=C["bg"], fg=C["fg"], font=self._ui_font, padx=10).pack(side=tk.RIGHT)

    def _build_menu(self):
        mc = {
            "bg": C["menu_bg"],
            "fg": C["fg"],
            "activebackground": C["btn_hover"],
            "activeforeground": C["fg"],
        }
        bar = tk.Menu(self, **mc)
        fm = tk.Menu(bar, tearoff=0, **mc)
        fm.add_command(label="New", accelerator="Ctrl+N", command=self._new_file)
        fm.add_command(label="Open", accelerator="Ctrl+O", command=self._open_file)
        fm.add_separator()
        fm.add_command(label="Save", accelerator="Ctrl+S", command=self._save_file)
        fm.add_command(label="Save As", accelerator="Ctrl+Shift+S", command=self._save_as)
        fm.add_separator()
        fm.add_command(label="Open in EMU8086", accelerator="F5", command=self._run_emu)
        fm.add_separator()
        fm.add_command(label="Exit", command=self._on_close)
        bar.add_cascade(label="File", menu=fm)
        em = tk.Menu(bar, tearoff=0, **mc)
        em.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: self._text.edit_undo())
        em.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: self._text.edit_redo())
        em.add_separator()
        em.add_command(
            label="Select All",
            accelerator="Ctrl+A",
            command=lambda: self._text.tag_add(tk.SEL, "1.0", tk.END),
        )
        bar.add_cascade(label="Edit", menu=em)
        hm = tk.Menu(bar, tearoff=0, **mc)
        hm.add_command(label="About", command=self._about)
        bar.add_cascade(label="Help", menu=hm)
        self.config(menu=bar)

    def _bind_keys(self):
        self.bind("<Control-n>", lambda e: self._new_file())
        self.bind("<Control-o>", lambda e: self._open_file())
        self.bind("<Control-s>", lambda e: self._save_file())
        self.bind("<Control-S>", lambda e: self._save_as())
        self.bind("<F5>", lambda e: self._run_emu())
        self._text.bind("<KeyRelease>", self._on_key)
        self._text.bind("<Return>", self._on_enter)
        self._text.bind("<ButtonRelease-1>", lambda e: self._update_pos())
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_key(self, event=None):
        self._modified = True
        self._update_pos()
        self._update_segment_and_map()
        self._line_nums.redraw()
        self._highlighter.highlight()
        if self._lint_job:
            self.after_cancel(self._lint_job)
        self._lint_job = self.after(self.LINT_DELAY_MS, self._run_lint)

    def _on_enter(self, event=None):
        if self._autosave_on_enter:
            self._autosave.save_now(trigger="enter")
        return None

    def _update_pos(self):
        idx = self._text.index(tk.INSERT)
        ln, col = idx.split(".")
        self._st_pos.config(text=f"Ln {ln}  Col {int(col) + 1}")
        self._update_segment_and_map()

    def _update_segment_and_map(self):
        pass

    def _run_lint(self):
        errors = self._linter.lint(self._content())
        self._err_panel.show(errors)
        self._text.tag_remove("error_line", "1.0", tk.END)
        self._text.tag_remove("warn_line", "1.0", tk.END)
        for e in errors:
            ln = e["line"]
            tag = "error_line" if e["severity"] == "error" else "warn_line"
            self._text.tag_add(tag, f"{ln}.0", f"{ln}.end")
        n_err = sum(1 for e in errors if e["severity"] == "error")
        n_warn = sum(1 for e in errors if e["severity"] == "warning")
        if n_err:
            self._st_err.config(text=f"{n_err} error(s)", fg=C["err_ul"])
        elif n_warn:
            self._st_err.config(text=f"{n_warn} warning(s)", fg=C["warn_ul"])
        else:
            self._st_err.config(text="No errors", fg=C["fg"])

    def _content(self) -> str:
        return self._text.get("1.0", tk.END)

    def _new_file(self, silent=False):
        if not silent and self._modified:
            if not messagebox.askyesno("New File", "Discard unsaved changes?"):
                return
        self._text.delete("1.0", tk.END)
        self._text.insert("1.0", _TEMPLATE)
        self._filepath = None
        self._modified = False
        self._set_title("Untitled.asm")
        self._highlighter.highlight()
        self._run_lint()
        self._line_nums.redraw()
        self._update_segment_and_map()

    def _open_file(self):
        if self._modified:
            if not messagebox.askyesno("Open File", "Discard unsaved changes?"):
                return
        path = filedialog.askopenfilename(
            title="Open ASM file",
            filetypes=[("Assembly Files", "*.asm"), ("All Files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as e:
            messagebox.showerror("Open Error", str(e))
            return
        self._text.delete("1.0", tk.END)
        self._text.insert("1.0", content)
        self._filepath = path
        self._modified = False
        self._set_title(os.path.basename(path))
        self._highlighter.highlight()
        self._run_lint()
        self._line_nums.redraw()
        self._update_segment_and_map()

    def _save_file(self):
        if not self._filepath:
            self._save_as()
            return
        self._write(self._filepath)

    def _save_as(self):
        path = filedialog.asksaveasfilename(
            title="Save ASM file",
            defaultextension=".asm",
            filetypes=[("Assembly Files", "*.asm"), ("All Files", "*.*")],
        )
        if not path:
            return
        self._filepath = path
        self._write(path)

    def _write(self, path: str):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._content())
            self._modified = False
            self._set_title(os.path.basename(path))
        except OSError as e:
            messagebox.showerror("Save Error", str(e))

    def _set_title(self, name: str):
        self.title(f"ASM Editor – {name}")
        self._st_file.config(text=name)

    def _run_emu(self):
        if not self._filepath:
            messagebox.showinfo("Save Required", "Please save the file first (Ctrl+S)\nbefore opening in EMU8086.")
            self._save_as()
            if not self._filepath:
                return
        else:
            self._write(self._filepath)
        ok, msg = self._bridge.launch(self._filepath)
        if not ok:
            messagebox.showerror("EMU8086 Error", msg)

    def _on_autosave_done(self, path: str, trigger: str):
        name = os.path.basename(path)
        icon = "Saved (Enter)" if trigger == "enter" else "Autosaved"
        self._save_indicator.config(text=f"{icon}: {name}", fg=C["fg"])
        self.after(2500, lambda: self._save_indicator.config(text=""))

    def _about(self):
        messagebox.showinfo(
            "About",
            "Assembly-Aware Text Editor\n"
            "Author: Sharvesh R V\n"
            "Roll No: 2403717672621045\n"
            "Subject: 20MSS46\n",
        )

    def _on_close(self):
        if self._modified:
            if not messagebox.askyesno("Quit", "You have unsaved changes. Quit anyway?"):
                return
        self._autosave.stop()
        self.destroy()

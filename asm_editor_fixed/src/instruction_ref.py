import tkinter as tk

_INSTRUCTIONS = {
    "AAA": ("8", "A C"),
    "AAD": ("60", "P Z S"),
    "AAM": ("83", "P Z S"),
    "AAS": ("8", "A C"),
    "ADC": ("3-4", "O S Z A P C"),
    "ADD": ("3-4", "O S Z A P C"),
    "AND": ("3-4", "O S Z P C"),
    "BOUND": ("10-13", "None"),
    "CALL": ("16-23", "None"),
    "CBW": ("2", "None"),
    "CLC": ("2", "C"),
    "CLD": ("2", "D"),
    "CLI": ("2", "I"),
    "CMC": ("2", "C"),
    "CMP": ("3-4", "O S Z A P C"),
    "CMPSB": ("22", "O S Z A P C"),
    "CMPSW": ("22", "O S Z A P C"),
    "CWD": ("5", "None"),
    "DAA": ("4", "A C"),
    "DAS": ("4", "A C"),
    "DEC": ("2-3", "O S Z A P"),
    "DIV": ("80-90", "O S Z A P C"),
    "ESC": ("2-8", "None"),
    "HLT": ("2", "None"),
    "IDIV": ("85-101", "O S Z A P C"),
    "IMUL": ("76-138", "O S Z A P C"),
    "IN": ("8-14", "None"),
    "INC": ("2-3", "O S Z A P"),
    "INT": ("51-55", "None"),
    "INTO": ("53", "O"),
    "IRET": ("24", "O S Z A P C"),
    "JA": ("16", "None"),
    "JAE": ("16", "None"),
    "JB": ("16", "None"),
    "JBE": ("16", "None"),
    "JC": ("16", "None"),
    "JCXZ": ("18", "None"),
    "JE": ("16", "None"),
    "JG": ("16", "None"),
    "JGE": ("16", "None"),
    "JL": ("16", "None"),
    "JLE": ("16", "None"),
    "JMP": ("15", "None"),
    "JNA": ("16", "None"),
    "JNAE": ("16", "None"),
    "JNB": ("16", "None"),
    "JNBE": ("16", "None"),
    "JNC": ("16", "None"),
    "JNE": ("16", "None"),
    "JNG": ("16", "None"),
    "JNGE": ("16", "None"),
    "JNL": ("16", "None"),
    "JNLE": ("16", "None"),
    "JNO": ("16", "None"),
    "JNP": ("16", "None"),
    "JNS": ("16", "None"),
    "JNZ": ("16", "None"),
    "JO": ("16", "None"),
    "JP": ("16", "None"),
    "JPE": ("16", "None"),
    "JPO": ("16", "None"),
    "JS": ("16", "None"),
    "JZ": ("16", "None"),
    "LAHF": ("2", "None"),
    "LDS": ("7", "None"),
    "LEA": ("2-4", "None"),
    "LES": ("7", "None"),
    "LOCK": ("2", "None"),
    "LODSB": ("12", "None"),
    "LODSW": ("12", "None"),
    "LOOP": ("17", "None"),
    "LOOPE": ("18", "None"),
    "LOOPNE": ("19", "None"),
    "LOOPNZ": ("19", "None"),
    "LOOPZ": ("18", "None"),
    "MOV": ("2-4", "None"),
    "MOVS": ("18", "None"),
    "MOVSB": ("18", "None"),
    "MOVSW": ("18", "None"),
    "MUL": ("70-77", "O S Z A P C"),
    "NEG": ("3", "O S Z A P C"),
    "NOP": ("3", "None"),
    "NOT": ("3", "None"),
    "OR": ("3-4", "O S Z P C"),
    "OUT": ("8-16", "None"),
    "POP": ("8", "None"),
    "POPF": ("8", "None"),
    "PUSH": ("10-16", "None"),
    "PUSHF": ("10", "None"),
    "RCL": ("8+", "O S Z A P C"),
    "RCR": ("8+", "O S Z A P C"),
    "REP": ("2", "None"),
    "REPE": ("2", "None"),
    "REPNE": ("2", "None"),
    "REPNZ": ("2", "None"),
    "REPZ": ("2", "None"),
    "RET": ("16-24", "None"),
    "RETF": ("17-25", "None"),
    "ROL": ("8+", "O S Z A P C"),
    "ROR": ("8+", "O S Z A P C"),
    "SAHF": ("4", "None"),
    "SAL": ("8+", "O S Z A P C"),
    "SAR": ("8+", "O S Z A P C"),
    "SBB": ("3-4", "O S Z A P C"),
    "SCASB": ("15", "O S Z A P C"),
    "SCASW": ("15", "O S Z A P C"),
    "SHL": ("8+", "O S Z A P C"),
    "SHR": ("8+", "O S Z A P C"),
    "STC": ("2", "C"),
    "STD": ("2", "D"),
    "STI": ("2", "I"),
    "STOSB": ("11", "None"),
    "STOSW": ("11", "None"),
    "SUB": ("3-4", "O S Z A P C"),
    "TEST": ("3-4", "O S Z A P C"),
    "WAIT": ("3+", "None"),
    "XCHG": ("3-4", "None"),
    "XLAT": ("11", "None"),
    "XOR": ("3-4", "O S Z P C"),
}

def lookup(mnemonic: str):
    m = mnemonic.strip().upper()
    return _INSTRUCTIONS.get(m)


class InstructionTooltip:

    def __init__(self, widget: tk.Text, bg: str, fg: str, font):
        self._w = widget
        self._bg = bg
        self._fg = fg
        self._font = font
        self._tip = None
        self._job = None
        self._delay = 220
        self._w.bind("<Motion>", self._on_motion, add=True)
        self._w.bind("<Leave>", self._hide, add=True)
        self._w.bind("<Button-1>", self._hide, add=True)

    def _word_at(self, line, col):
        if not line:
            return None
        if col >= len(line):
            col = len(line) - 1
        if col < 0:
            return None
        i = col
        while i > 0 and (line[i - 1].isalnum() or line[i - 1] in "@_?"):
            i -= 1
        j = col
        while j < len(line) and (line[j].isalnum() or line[j] in "@_?"):
            j += 1
        w = line[i:j]
        return w if w else None

    def _on_motion(self, event):
        if self._job:
            self._w.after_cancel(self._job)
            self._job = None
        self._hide()
        idx = self._w.index(f"@{event.x},{event.y}")
        line = self._w.get(f"{idx} linestart", f"{idx} lineend").rstrip("\n")
        col = int(idx.split(".")[1])
        tok = self._word_at(line, col)
        if not tok:
            return
        info = lookup(tok)
        if not info:
            return
        cyc, flags = info
        self._job = self._w.after(
            self._delay,
            lambda t=tok, cy=cyc, fl=flags: self._show(
                event.x_root, event.y_root, t, cy, fl
            ),
        )

    def _show(self, x, y, name, cyc, flags):
        self._hide()
        self._tip = tk.Toplevel(self._w)
        self._tip.wm_overrideredirect(True)
        self._tip.configure(bg=self._bg)
        txt = f"{name}\nClock cycles: {cyc}\nFlags: {flags}"
        lb = tk.Label(
            self._tip,
            text=txt,
            bg=self._bg,
            fg=self._fg,
            font=self._font,
            justify=tk.LEFT,
            padx=8,
            pady=6,
        )
        lb.pack()
        self._tip.geometry(f"+{x + 14}+{y + 18}")

    def _hide(self, event=None):
        if self._job:
            try:
                self._w.after_cancel(self._job)
            except tk.TclError:
                pass
            self._job = None
        if self._tip:
            try:
                self._tip.destroy()
            except tk.TclError:
                pass
            self._tip = None

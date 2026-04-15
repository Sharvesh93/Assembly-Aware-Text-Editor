import re
import tkinter as tk
from src.asm_keywords import ALL_MNEMONICS, ALL_REGS, DIRECTIVES


def _kw_pattern(words):
    escaped = sorted(words, key=len, reverse=True)
    return r"\b(" + "|".join(re.escape(w) for w in escaped) + r")\b"


_TOKENS = [
    (re.compile(r";.*$", re.MULTILINE), "comment"),
    (re.compile(r"'[^'\n]*'|\"[^\"\n]*\""), "string"),
    (re.compile(r"\b[0-9A-Fa-f]+[Hh]\b|\b0[Xx][0-9A-Fa-f]+\b"), "num_hex"),
    (re.compile(r"\b[01]+[Bb]\b"), "num_bin"),
    (re.compile(r"\b\d+\b"), "num_dec"),
    (re.compile(r"^[ \t]*([A-Za-z_@][A-Za-z0-9_@?]*)\s*:", re.MULTILINE), "label"),
    (re.compile(_kw_pattern(DIRECTIVES), re.IGNORECASE), "directive"),
    (re.compile(_kw_pattern(ALL_MNEMONICS), re.IGNORECASE), "mnemonic"),
    (re.compile(_kw_pattern(ALL_REGS), re.IGNORECASE), "register"),
    (re.compile(r"[\[\]+\-*]"), "operator"),
]

_COLOURS = {
    "comment": "#888888",
    "string": "#f2c2ff",
    "num_hex": "#ffcc66",
    "num_bin": "#ffcc66",
    "num_dec": "#ffcc66",
    "label": "#3ddbd9",
    "directive": "#be95ff",
    "mnemonic": "#78a9ff",
    "register": "#ff7eb6",
    "operator": "#08bdba",
}


class SyntaxHighlighter:
    def __init__(self, text: tk.Text):
        self.text = text
        for tag, colour in _COLOURS.items():
            self.text.tag_configure(tag, foreground=colour)

    def highlight(self, event=None):
        content = self.text.get("1.0", tk.END)
        for tag in _COLOURS:
            self.text.tag_remove(tag, "1.0", tk.END)
        for regex, tag in _TOKENS:
            for m in regex.finditer(content):
                s = f"1.0 + {m.start()} chars"
                e = f"1.0 + {m.end()} chars"
                self.text.tag_add(tag, s, e)
        self.text.tag_raise("error_line")
        self.text.tag_raise("warn_line")

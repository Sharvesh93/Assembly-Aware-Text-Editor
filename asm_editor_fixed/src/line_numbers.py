import tkinter as tk


class LineNumbers(tk.Canvas):
    WIDTH = 52

    def __init__(self, parent, text: tk.Text, **kw):
        self._fg = kw.pop("fg", "#ffffff")
        self._font = kw.pop("font", ("Poppins", 10))
        super().__init__(parent, width=self.WIDTH, highlightthickness=0, bd=0, **kw)
        self._text = text
        for event in ("<Configure>", "<<Modified>>", "<MouseWheel>", "<Button-4>", "<Button-5>"):
            self._text.bind(event, lambda e: self.after(5, self.redraw))

    def redraw(self, *_):
        self.delete("all")
        i = self._text.index("@0,0")
        while True:
            di = self._text.dlineinfo(i)
            if di is None:
                break
            y = di[1]
            line = i.split(".")[0]
            self.create_text(
                self.WIDTH - 6,
                y,
                anchor=tk.NE,
                text=line,
                fill=self._fg,
                font=self._font,
            )
            nxt = self._text.index(f"{i}+1line")
            if nxt == i:
                break
            i = nxt

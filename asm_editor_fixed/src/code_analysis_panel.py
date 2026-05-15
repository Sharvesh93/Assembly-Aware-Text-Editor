"""
Code Analysis Panel UI
Displays real-time analysis of assembly code in a separate panel
"""

import tkinter as tk
from tkinter import ttk
from src.code_analyzer import CodeAnalyzer


class CodeAnalysisPanel(tk.Frame):
    """Panel displaying code analysis and statistics"""

    def __init__(self, parent, text_widget, font_ui, font_small, bg, fg):
        """
        Initialize analysis panel
        
        Args:
            parent: Parent widget
            text_widget: The text editor widget to analyze
            font_ui: UI font
            font_small: Small font for details
            bg: Background color
            fg: Foreground color
        """
        super().__init__(parent, bg=bg, relief=tk.FLAT, bd=0)
        self._text = text_widget
        self._analyzer = CodeAnalyzer()
        self._bg = bg
        self._fg = fg
        self._font_ui = font_ui
        self._font_small = font_small
        self._analysis_job = None

        self._build_ui()

    def _build_ui(self):
        """Build the UI components"""
        # Header with refresh button
        header = tk.Frame(self, bg=self._bg, height=32)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="Code Analysis",
            bg=self._bg,
            fg=self._fg,
            font=self._font_ui,
            padx=10,
            pady=4,
        )
        title.pack(side=tk.LEFT)

        refresh_btn = tk.Button(
            header,
            text="⟳ Refresh",
            command=self._on_refresh,
            bg="#2b2f55",
            fg=self._fg,
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=2,
            font=self._font_small,
            cursor="hand2",
        )
        refresh_btn.pack(side=tk.RIGHT, padx=5, pady=2)

        # Notebook for tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self._bg, borderwidth=0)
        style.configure('TNotebook.Tab', background=self._bg, foreground=self._fg)
        style.configure('TFrame', background=self._bg)
        style.configure('TLabel', background=self._bg, foreground=self._fg)
        
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Statistics tab
        self._stats_frame = tk.Frame(self._notebook, bg=self._bg)
        self._notebook.add(self._stats_frame, text="Statistics")
        self._build_stats_tab()

        # Labels tab
        self._labels_frame = tk.Frame(self._notebook, bg=self._bg)
        self._notebook.add(self._labels_frame, text="Labels")
        self._build_labels_tab()

        # Registers tab
        self._regs_frame = tk.Frame(self._notebook, bg=self._bg)
        self._notebook.add(self._regs_frame, text="Registers")
        self._build_registers_tab()

        # Issues tab
        self._issues_frame = tk.Frame(self._notebook, bg=self._bg)
        self._notebook.add(self._issues_frame, text="Issues")
        self._build_issues_tab()

    def _build_stats_tab(self):
        """Build statistics tab"""
        canvas = tk.Canvas(
            self._stats_frame, bg=self._bg, highlightthickness=0, relief=tk.FLAT
        )
        scrollbar = tk.Scrollbar(self._stats_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self._bg)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self._stats_labels = {}
        
        # Lines
        tk.Label(scrollable_frame, text="═ Lines ═", bg=self._bg, fg=self._fg, 
                font=self._font_ui, anchor="w").pack(fill=tk.X, padx=5, pady=(5, 3))
        
        for key in ["total_lines", "code_lines", "comment_lines", "blank_lines"]:
            frame = tk.Frame(scrollable_frame, bg=self._bg)
            frame.pack(fill=tk.X, padx=10, pady=1)
            label = tk.Label(frame, text=f"{key.replace('_', ' ').title()}: ", 
                           bg=self._bg, fg=self._fg, font=self._font_small)
            label.pack(side=tk.LEFT)
            val_label = tk.Label(frame, text="0", bg=self._bg, fg="#9DC183", 
                               font=self._font_small, anchor="e")
            val_label.pack(side=tk.RIGHT)
            self._stats_labels[key] = val_label

        # Instructions
        tk.Label(scrollable_frame, text="═ Instructions ═", bg=self._bg, fg=self._fg,
                font=self._font_ui, anchor="w").pack(fill=tk.X, padx=5, pady=(10, 3))
        
        for key in ["total_instructions", "unique_instructions"]:
            frame = tk.Frame(scrollable_frame, bg=self._bg)
            frame.pack(fill=tk.X, padx=10, pady=1)
            label = tk.Label(frame, text=f"{key.replace('_', ' ').title()}: ",
                           bg=self._bg, fg=self._fg, font=self._font_small)
            label.pack(side=tk.LEFT)
            val_label = tk.Label(frame, text="0", bg=self._bg, fg="#9DC183",
                               font=self._font_small, anchor="e")
            val_label.pack(side=tk.RIGHT)
            self._stats_labels[key] = val_label

        tk.Label(scrollable_frame, text="Top Instructions:", bg=self._bg, fg=self._fg,
                font=self._font_small).pack(fill=tk.X, padx=10, pady=(5, 2))
        self._top_instrs_label = tk.Label(scrollable_frame, text="", bg=self._bg,
                                         fg="#9DC183", font=self._font_small,
                                         justify=tk.LEFT)
        self._top_instrs_label.pack(fill=tk.X, padx=20, pady=2)

        # Size
        tk.Label(scrollable_frame, text="═ Size ═", bg=self._bg, fg=self._fg,
                font=self._font_ui, anchor="w").pack(fill=tk.X, padx=5, pady=(10, 3))
        
        for key in ["estimated_code_size", "data_segment_size"]:
            frame = tk.Frame(scrollable_frame, bg=self._bg)
            frame.pack(fill=tk.X, padx=10, pady=1)
            label = tk.Label(frame, text=f"{key.replace('_', ' ').title()}: ",
                           bg=self._bg, fg=self._fg, font=self._font_small)
            label.pack(side=tk.LEFT)
            val_label = tk.Label(frame, text="0 bytes", bg=self._bg, fg="#9DC183",
                               font=self._font_small, anchor="e")
            val_label.pack(side=tk.RIGHT)
            self._stats_labels[key] = val_label

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_labels_tab(self):
        """Build labels tab"""
        canvas = tk.Canvas(
            self._labels_frame, bg=self._bg, highlightthickness=0, relief=tk.FLAT
        )
        scrollbar = tk.Scrollbar(self._labels_frame, orient=tk.VERTICAL, command=canvas.yview)
        self._labels_content = tk.Frame(canvas, bg=self._bg)

        self._labels_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self._labels_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_registers_tab(self):
        """Build registers tab"""
        canvas = tk.Canvas(
            self._regs_frame, bg=self._bg, highlightthickness=0, relief=tk.FLAT
        )
        scrollbar = tk.Scrollbar(self._regs_frame, orient=tk.VERTICAL, command=canvas.yview)
        self._regs_content = tk.Frame(canvas, bg=self._bg)

        self._regs_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self._regs_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_issues_tab(self):
        """Build issues tab"""
        canvas = tk.Canvas(
            self._issues_frame, bg=self._bg, highlightthickness=0, relief=tk.FLAT
        )
        scrollbar = tk.Scrollbar(self._issues_frame, orient=tk.VERTICAL, command=canvas.yview)
        self._issues_content = tk.Frame(canvas, bg=self._bg)

        self._issues_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self._issues_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh(self):
        """Refresh analysis from text widget"""
        if self._analysis_job:
            self.after_cancel(self._analysis_job)
        self._analysis_job = self.after(200, self._do_refresh)

    def _on_refresh(self):
        """Handle refresh button click"""
        self._do_refresh()

    def _do_refresh(self):
        """Perform actual refresh"""
        content = self._text.get("1.0", tk.END)
        report = self._analyzer.analyze(content)

        # Update statistics
        self._stats_labels["total_lines"].config(text=str(report["total_lines"]))
        self._stats_labels["code_lines"].config(text=str(report["code_lines"]))
        self._stats_labels["comment_lines"].config(text=str(report["comment_lines"]))
        self._stats_labels["blank_lines"].config(text=str(report["blank_lines"]))
        self._stats_labels["total_instructions"].config(text=str(report["total_instructions"]))
        self._stats_labels["unique_instructions"].config(text=str(report["unique_instructions"]))
        self._stats_labels["estimated_code_size"].config(
            text=f"{report['estimated_code_size']} bytes"
        )
        self._stats_labels["data_segment_size"].config(
            text=f"{report['data_segment_size']} bytes"
        )

        # Top instructions
        if report["top_instructions"]:
            instr_text = "\n".join(
                f"{instr}: {count}" for instr, count in report["top_instructions"]
            )
            self._top_instrs_label.config(text=instr_text)
        else:
            self._top_instrs_label.config(text="(none)")

        # Update labels tab
        self._update_labels_tab(report)

        # Update registers tab
        self._update_registers_tab(report)

        # Update issues tab
        self._update_issues_tab(report)

    def _update_labels_tab(self, report: dict):
        """Update labels tab content"""
        for widget in self._labels_content.winfo_children():
            widget.destroy()

        if not report["label_list"]:
            tk.Label(self._labels_content, text="(No labels defined)",
                    bg=self._bg, fg=self._fg, font=self._font_small).pack(padx=10, pady=5)
            return

        tk.Label(self._labels_content, text=f"Defined: {len(report['label_list'])}",
                bg=self._bg, fg=self._fg, font=self._font_ui).pack(fill=tk.X, padx=5, pady=3)

        for label, line in sorted(report["label_list"].items()):
            frame = tk.Frame(self._labels_content, bg=self._bg)
            frame.pack(fill=tk.X, padx=10, pady=2)
            
            refs = len(report["labels_referenced"].get(label, []))
            ref_color = "#ffff66" if refs == 0 else "#9DC183"
            
            tk.Label(frame, text=f"{label} ", bg=self._bg, fg=self._fg,
                    font=self._font_small).pack(side=tk.LEFT)
            tk.Label(frame, text=f"Line {line}",  bg=self._bg, fg="#7a7a7a",
                    font=self._font_small).pack(side=tk.LEFT)
            tk.Label(frame, text=f"({refs} refs)", bg=self._bg, fg=ref_color,
                    font=self._font_small).pack(side=tk.RIGHT)

    def _update_registers_tab(self, report: dict):
        """Update registers tab content"""
        for widget in self._regs_content.winfo_children():
            widget.destroy()

        if not report["register_usage"]:
            tk.Label(self._regs_content, text="(No registers used)",
                    bg=self._bg, fg=self._fg, font=self._font_small).pack(padx=10, pady=5)
            return

        tk.Label(self._regs_content, text=f"Used: {report['unique_registers']}",
                bg=self._bg, fg=self._fg, font=self._font_ui).pack(fill=tk.X, padx=5, pady=3)

        for reg, count in report["register_usage"]:
            frame = tk.Frame(self._regs_content, bg=self._bg)
            frame.pack(fill=tk.X, padx=10, pady=2)
            
            tk.Label(frame, text=f"{reg}", bg=self._bg, fg=self._fg,
                    font=self._font_small, width=6, anchor="w").pack(side=tk.LEFT)
            
            # Simple bar chart
            bar_width = min(count * 2, 50)
            bar = tk.Canvas(frame, width=bar_width, height=12, bg=self._bg,
                           highlightthickness=0)
            bar.pack(side=tk.LEFT, padx=5)
            bar.create_rectangle(0, 0, bar_width, 12, fill="#276825", outline="#276825")
            
            tk.Label(frame, text=f"×{count}", bg=self._bg, fg="#9DC183",
                    font=self._font_small).pack(side=tk.LEFT)

    def _update_issues_tab(self, report: dict):
        """Update issues tab content"""
        for widget in self._issues_content.winfo_children():
            widget.destroy()

        issues_found = False

        # Undefined jumps
        if report["undefined_jumps"]:
            issues_found = True
            tk.Label(self._issues_content, text="⚠ Undefined Jump Targets",
                    bg=self._bg, fg="#ffff66", font=self._font_ui).pack(fill=tk.X, padx=5, pady=(5, 3))
            for label in report["undefined_jumps"]:
                tk.Label(self._issues_content, text=f"  → {label}",
                        bg=self._bg, fg="#ff9999", font=self._font_small).pack(fill=tk.X, padx=15, pady=1)

        # Unreferenced labels
        if report["unreferenced_labels"]:
            issues_found = True
            if report["undefined_jumps"]:
                tk.Label(self._issues_content, text="", bg=self._bg).pack()
            
            tk.Label(self._issues_content, text="ℹ Unreferenced Labels",
                    bg=self._bg, fg="#9DC183", font=self._font_ui).pack(fill=tk.X, padx=5, pady=(5, 3))
            for label in report["unreferenced_labels"]:
                line = report["label_list"].get(label, "?")
                tk.Label(self._issues_content, text=f"  → {label} (line {line})",
                        bg=self._bg, fg="#9DC183", font=self._font_small).pack(fill=tk.X, padx=15, pady=1)

        if not issues_found:
            tk.Label(self._issues_content, text="✓ No issues found",
                    bg=self._bg, fg="#9DC183", font=self._font_small).pack(padx=10, pady=10)

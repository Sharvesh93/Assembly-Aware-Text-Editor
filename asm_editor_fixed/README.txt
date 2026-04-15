================================================================
  ASSEMBLY-AWARE TEXT EDITOR
  Real-Time Error Detection + Automatic Saving + EMU8086
================================================================
  Author  : Sharvesh R V
  Roll No : 2403717672621045
  Subject : 20MSS46 – Microprocessor and Microcontroller Lab
================================================================

PROJECT STRUCTURE
-----------------
asm_editor/
  main.py                   ← Entry point  (run this)
  config.ini                ← EMU8086 path + editor settings
  sample_program.asm        ← Sample file to test the editor
  src/
    __init__.py
    editor_app.py           ← Main Tkinter window (all modules wired)
    asm_keywords.py         ← Module 1: Syntax Engine keyword DB
    addr_validator.py       ← Module 2: Addressing Mode Validator
    linter.py               ← Module 3: Real-Time Diagnostic Linter
    syntax_highlighter.py   ← Colour tokeniser
    autosave.py             ← Autosave on Enter + timer
    emu_bridge.py           ← EMU8086 launcher
    error_panel.py          ← Diagnostics panel widget
    line_numbers.py         ← Line number gutter


HOW TO RUN
----------
Requirements:
  • Python 3.9 or higher
  • Tkinter (included with Python on Windows/macOS)
  • Linux only: sudo apt install python3-tk

Steps:
  1. Open a terminal / command prompt.
  2. Navigate to the asm_editor/ folder:
       cd path\to\asm_editor
  3. Run:
       python main.py


CONFIGURE EMU8086 PATH
----------------------
Open config.ini in Notepad and set the correct path:

  [emu8086]
  path = C:\emu8086\emu8086.exe

If EMU8086 is installed elsewhere, update this path.
The editor will still work (linting, highlighting, autosave)
even if EMU8086 is not installed.


FEATURES
--------

1. REAL-TIME ERROR DETECTION (fires 400 ms after last keystroke)
   Errors flagged:
     ✖  Unknown / misspelled mnemonic
     ✖  MOV with two memory operands
     ✖  MOV CS as destination (CS cannot be written to)
     ✖  MOV segment register ← immediate value
     ✖  8-bit / 16-bit register size mismatch in MOV
     ✖  Instruction with missing operands (PUSH, ADD, etc.)
     ✖  Instruction with too many operands (NOP AX, etc.)
     ✖  Duplicate label definitions
     ✖  Reserved word used as a label
     ✖  Invalid register in memory address ([AX+SI] is illegal)
     ✖  Missing ] in memory operand
   Warnings:
     ⚠  Undefined jump/call label target
     ⚠  .DATA after .CODE (directive order issue)

2. AUTOSAVE ON ENTER  ★ KEY FEATURE ★
   Every time you press Enter (Carriage Return), the file is
   saved automatically. No manual Ctrl+S needed while typing.
   • If no file is open yet → saved to a temp recovery file
   • Confirmation shown in toolbar: "↵ Saved: filename.asm"
   • Fallback timer also saves every 10 seconds

3. SYNTAX HIGHLIGHTING
   Blue     Mnemonics      MOV, ADD, JMP, LOOP …
   Pink     Registers      AX, BX, CS, SI …
   Purple   Directives     .MODEL, DB, SEGMENT, EQU …
   Cyan     Labels         MAIN:, COUNT_LOOP: …
   Green    Strings        'Hello$'
   Orange   Numbers        0FFh, 1234, 1010b
   Grey     Comments       ; any comment text
   Teal     Operators      [ ] + -

4. DIAGNOSTICS PANEL (bottom of window)
   • Lists all errors and warnings with line numbers.
   • Double-click any row → jumps editor cursor to that line.
   • Error lines are underlined red in the editor.
   • Warning lines are underlined yellow.

5. OPEN IN EMU8086 (toolbar button or F5)
   • Saves the current file.
   • Launches EMU8086 with the file already loaded.
   • You assemble and run from within EMU8086 as normal.

6. FILE OPERATIONS
   Ctrl+N       New file (with default 8086 template)
   Ctrl+O       Open .asm file
   Ctrl+S       Save
   Ctrl+Shift+S Save As
   F5           Open in EMU8086


MODULE MAPPING
--------------
Abstract Module              Implemented In
────────────────────────────────────────────────────────
Module 1 – Syntax Engine     src/asm_keywords.py
                             src/syntax_highlighter.py
Module 2 – Addr Validator    src/addr_validator.py
                             src/linter.py (MOV checks)
Module 3 – Linter            src/linter.py
Module 4 – Segmentation      src/linter.py (directive order)
Module 5 – Ref Overlay       src/error_panel.py (messages)
Module 6 – Tool Bridge       src/emu_bridge.py
Module 7 – Memory Visualizer (planned)


TESTING THE LINTER
------------------
Open sample_program.asm and uncomment the lines at the
bottom of the file to trigger specific errors. Each error
description is written as a comment next to the line.

================================================================

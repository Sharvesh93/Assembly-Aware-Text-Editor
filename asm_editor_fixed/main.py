import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.editor_app import AsmEditorApp

if __name__ == "__main__":
    app = AsmEditorApp()
    app.mainloop()

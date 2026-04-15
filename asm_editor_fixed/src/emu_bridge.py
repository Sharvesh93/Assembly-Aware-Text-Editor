import os
import subprocess
from typing import Tuple


class EmuBridge:
    def __init__(self, emu_path: str):
        self.emu_path = emu_path

    def is_available(self) -> bool:
        return os.path.isfile(self.emu_path)

    def launch(self, filepath: str) -> Tuple[bool, str]:
        if not self.is_available():
            return False, f"EMU8086 not found at:\n  {self.emu_path}\n\nPlease update the path in config.ini"
        if not filepath or not os.path.isfile(filepath):
            return False, "No file to open. Save the file first (Ctrl+S)."
        try:
            subprocess.Popen(
                [self.emu_path, filepath],
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
            )
            return True, f"Opened in EMU8086:\n  {filepath}"
        except Exception as exc:
            return False, f"Failed to launch EMU8086:\n  {exc}"

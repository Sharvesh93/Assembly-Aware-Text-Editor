import os
import tempfile
from typing import Callable, Optional

RECOVERY_NAME = ".asm_editor_recovery.asm"


class AutoSave:
    def __init__(
        self,
        get_content: Callable[[], str],
        get_filepath: Callable[[], Optional[str]],
        on_save: Optional[Callable[[str, str], None]] = None,
        fallback_ms: int = 10_000,
    ):
        self._get_content = get_content
        self._get_filepath = get_filepath
        self._on_save = on_save
        self._fallback_ms = fallback_ms
        self._root = None
        self._after_id = None
        self._recovery = os.path.join(tempfile.gettempdir(), RECOVERY_NAME)

    def start(self, root):
        self._root = root
        self._schedule()

    def stop(self):
        if self._after_id and self._root:
            try:
                self._root.after_cancel(self._after_id)
            except Exception:
                pass
        self._cleanup_recovery()

    def save_now(self, trigger: str = "enter"):
        self._do_save(trigger)

    def _schedule(self):
        if self._root:
            self._after_id = self._root.after(self._fallback_ms, self._tick)

    def _tick(self):
        self._do_save("timer")
        self._schedule()

    def _do_save(self, trigger: str):
        content = self._get_content()
        path = self._get_filepath()
        target = path if path else self._recovery
        try:
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            if self._on_save:
                self._on_save(target, trigger)
        except OSError:
            pass

    def _cleanup_recovery(self):
        try:
            if os.path.exists(self._recovery):
                os.remove(self._recovery)
        except OSError:
            pass

    @property
    def recovery_path(self):
        return self._recovery

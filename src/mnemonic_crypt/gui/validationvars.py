from typing import Callable

from tkinter import StringVar

class DataValidationError(Exception):
    msg: str

    def __init__(self, msg: str):
        self.msg = msg

    @staticmethod
    def raise_from_parent(parent: Exception):
        msg = str(parent)
        e = DataValidationError(msg)
        raise e from parent

class StringValidationVar(StringVar):
    write_cb: list[Callable[[str, str, str], None]]
    valid: bool
    error_msg: StringVar

    def __init__(self, write_cb: Callable[[str, str, str], None], parent = None, value = None, name = None):
        super().__init__(parent, value, name)

        self.write_cb = [write_cb]
        self.valid = True
        self.error_msg = StringVar(value="", name=f"{name}_error_str")

        self.trace_add("write", self._on_changed)

    def _on_changed(self, var_name: str, idx: str, mode: str) -> None:
        assert mode == "write"
        try:
            self.valid = True
            self.error_msg.set("")
            for cb in self.write_cb:
                cb(var_name, idx, mode)
        except DataValidationError as e:
            self.valid = False
            msg = e.msg
            msg = msg[0].upper() + msg[1:] + "."
            self.error_msg.set(msg)

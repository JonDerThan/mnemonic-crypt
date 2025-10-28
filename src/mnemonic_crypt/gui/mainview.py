from tkinter import ttk
from tkinter import Misc
import tkinter

from .mainviewmodel import MainViewModel
from .validationvars import StringValidationVar

class StringEntryWithValidation(ttk.Frame):
    def __init__(self, parent: Misc, textvariable: StringValidationVar):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)

        entry = ttk.Entry(self, textvariable=textvariable)
        entry.grid(column=0, row=0, sticky="new")

        entry_err = ttk.Label(
            self,
            font="TkSmallCaptionFont",
            foreground="red",
            textvariable=textvariable.error_msg
        )
        entry_err.grid(column=0, row=1, sticky="new")

class MainView:
    vm: MainViewModel
    mainframe: ttk.Frame

    def __init__(self, parent: Misc, viewmodel: MainViewModel):
        self.vm = viewmodel

        self.mainframe = ttk.Frame(parent, padding=10)
        self.mainframe.columnconfigure(1, weight=1)

        ttk.Label(self.mainframe, text="Plain data:").grid(
            column=0, row=0, sticky="nw")
        StringEntryWithValidation(self.mainframe, self.vm.plain_data_hex).grid(
            column=1, row=0, sticky="new")

        ttk.Label(self.mainframe, text="Plain mnemonic:").grid(
            column=0, row=1, sticky="nw")
        StringEntryWithValidation(self.mainframe, self.vm.plain_data_mnemonic).grid(
            column=1, row=1, sticky="new")

        ttk.Label(self.mainframe, text="Salt:").grid(
            column=0, row=2, sticky="nw")
        StringEntryWithValidation(self.mainframe, self.vm.salt_hex).grid(
            column=1, row=2, sticky="new")
        ttk.Button(self.mainframe, text="Rnd", command=self.vm.randomize_salt).grid(
            column=2, row=2, sticky="nw")

        ttk.Label(self.mainframe, text="Salt mnemonic:").grid(
            column=0, row=3, sticky="nw")
        StringEntryWithValidation(self.mainframe, self.vm.salt_mnemonic).grid(
            column=1, row=3, sticky="new")

        ttk.Label(self.mainframe, text="Password:").grid(
            column=0, row=4, sticky="nw")
        x = ttk.Entry(self.mainframe, textvariable=self.vm.password)
        x.grid(
            column=1, row=4, sticky="new")

        ttk.Checkbutton(self.mainframe, text="Encryption key generated", state="disabled", variable=self.vm.is_key_valid).grid(
            column=0, row=5, sticky="w")
        ttk.Button(self.mainframe, text="Generate", command=self.vm.update_key).grid(
            column=1, row=5, sticky="w")

        ttk.Label(self.mainframe, text="KDF paramaters:").grid(
            column=0, row=6, sticky="nw")
        ttk.Entry(self.mainframe, textvariable=self.vm.kdf_params).grid(
            column=1, row=6, sticky="new")

        ttk.Label(self.mainframe, text="Encrypted mnemonic:").grid(
            column=0, row=7, sticky="nw")
        StringEntryWithValidation(self.mainframe, self.vm.encrypted_mnemonic).grid(
            column=1, row=7, sticky="new")

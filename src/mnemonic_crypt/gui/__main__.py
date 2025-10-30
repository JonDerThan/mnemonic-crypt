import tkinter as tk
from tkinter import ttk

from mnemonic_crypt.mnemonics import MnemonicConverter
from mnemonic_crypt.gui.mainview import MainView
from mnemonic_crypt.gui.mainviewmodel import MainViewModel


def main():
    root = tk.Tk()
    root.title("Test title")
    root.geometry("1200x600+100+100")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    mnemonic_conv = MnemonicConverter.from_bip39_file()
    vm = MainViewModel(mnemonic_conv)
    mainview = MainView(root, vm)
    mainview.mainframe.grid(column=0, row=0, sticky="nwes")

    root.mainloop()

if __name__ == "__main__":
    main()

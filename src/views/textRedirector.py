import tkinter as tk


class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, message):
        self.widget.configure(state="normal")
        self.widget.insert(tk.END, message, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see(tk.END)

    def flush(self):
        pass

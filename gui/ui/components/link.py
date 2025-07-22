import customtkinter as ctk

class Link(ctk.CTkLabel):
    def __init__(self, master, text: str, command=None, **kwargs):
        super().__init__(master, text=text, font=("Helvetica", 12), text_color="white", cursor="hand2", **kwargs)
        self.pack()
        if command:
            self.bind("<Button-1>", lambda e: command())
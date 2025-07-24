import customtkinter as ctk
from ui.atoms.button import Button

class Modal(ctk.CTkToplevel):
    def __init__(self, parent, child_widget_factory, margin=20, **kwargs):
        super().__init__(parent)
        self.withdraw()
        self.overrideredirect(True)
        self.configure(fg_color="#FFFFFF")

        # calculate position
        parent.update_idletasks() 
        root_x = parent.winfo_rootx()
        root_y = parent.winfo_rooty()
        root_w = parent.winfo_width()
        
        x = root_x + root_w + margin  
        y = root_y 

        self.geometry(f"+{x}+{y}")
        self.transient(parent)  
        self.grab_set()         

        self.modal_frame = ctk.CTkFrame(self)
        self.modal_frame.configure(fg_color="#FFFFFF")
        self.modal_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.modal_frame.pack_propagate(True)

        self.modal_frame.grid_rowconfigure(0, weight=0)
        self.modal_frame.grid_rowconfigure(1, weight=1)
        self.modal_frame.grid_columnconfigure(0, weight=1)

        # close button
        close_btn = Button(self.modal_frame, type="white", text="X", width=12, height=12, command=self.close_modal)
        close_btn.grid(row=0, column=0, sticky="ne")

        # content area
        content = child_widget_factory(self.modal_frame, **kwargs)
        content.grid(row=1, column=0, sticky="nsew")

        # bind escape key to close modal
        self.bind("<Escape>", lambda e: self.close_modal())

        self.deiconify()

    def close_modal(self):
        self.destroy()

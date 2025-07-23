import customtkinter as ctk
from ui.atoms.button import Button

class Modal(ctk.CTkToplevel):
    def __init__(self, parent, child_widget_factory, width=300, height=200, margin=20):
        super().__init__(parent)
        self.withdraw()
        self.overrideredirect(True)

        # set the size and position of the modal
        parent.update_idletasks() 
        root_x = parent.winfo_rootx()
        root_y = parent.winfo_rooty()
        root_w = parent.winfo_width()
        root_h = parent.winfo_height()

        # calculate position
        x = root_x + root_w + margin  
        y = root_y + (root_h // 2) - (height // 2)  

        self.geometry(f"{width}x{height}+{x}+{y}")
        self.transient(parent)  
        self.grab_set()         

        self.modal_frame = ctk.CTkFrame(self)
        self.modal_frame.configure(fg_color="#FFFFFF")
        self.modal_frame.pack(expand=True, fill="both", padx=2, pady=2)
        self.modal_frame.grid_rowconfigure(0, weight=0)
        self.modal_frame.grid_rowconfigure(1, weight=1)
        self.modal_frame.grid_columnconfigure(0, weight=1)

        # close button
        close_btn = Button(self.modal_frame, type="white", text="X", width=12, height=12, command=self.close_modal)
        close_btn.grid(row=0, column=0, sticky="ne", padx=5, pady=5)

        # content area
        content = child_widget_factory(self.modal_frame)
        content.grid(row=1, column=0, sticky="nsew")

        self.deiconify()    

    def close_modal(self):
        self.destroy()

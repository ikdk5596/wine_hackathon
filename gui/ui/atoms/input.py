import customtkinter as ctk

class Input(ctk.CTkEntry):
    def __init__(self, master, placeholder: str = "", **kwargs):
        super().__init__(
            master,
            placeholder_text=placeholder,
            height=40,
            corner_radius=10,
            font=("Helvetica", 14),    
            text_color="#333333",      
            **kwargs
        )

    def clear(self):
        """Clear the input field."""
        self.delete(0, ctk.END)
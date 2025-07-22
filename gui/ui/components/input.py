import customtkinter as ctk

class Input(ctk.CTkEntry):
    def __init__(self, master, placeholder: str = "", **kwargs):
        super().__init__(
            master,
            placeholder_text=placeholder,
            height=40,
            corner_radius=10,
            font=("Helvetica", 14),       # ✅ 글자 크기 설정
            text_color="#333333",         # ✅ 전경색 (글자색) 설정
            **kwargs
        )
        self.pack(pady=10, padx=40, fill="x")
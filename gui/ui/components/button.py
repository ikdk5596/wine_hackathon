import customtkinter as ctk

class Button(ctk.CTkButton):
    def __init__(self, master, text: str, command=None, type: str = "primary", **kwargs):
        style = self._get_style(type)

        super().__init__(
            master,
            text=text,
            command=command,
            height=38,
            corner_radius=8,
            fg_color=style["fg_color"],
            hover_color=style["hover_color"],
            text_color=style["text_color"],
            font=("Helvetica", 15, "bold"),  # ✅ 폰트 크기/굵기 설정
            **kwargs
        )

        self.pack(pady=(30, 10))

    def _get_style(self, type: str):
        if type == "white":
            return {
                "fg_color": "#ffffff",
                "hover_color": "#f0f0f0",
                "text_color": "#333333"
            }
        else:  # default: primary
            return {
                "fg_color": "#5670f6",
                "hover_color": "#3450f0",
                "text_color": "#ffffff"
            }

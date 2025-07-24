import customtkinter as ctk

class Button(ctk.CTkButton):
    def __init__(self, master, text: str, height: int = 38, command=None, type: str = "primary", **kwargs):
        style = self._get_style(type)

        super().__init__(
            master,
            text=text,
            command=command,
            height=height,
            corner_radius=8,
            fg_color=style["fg_color"],
            hover_color=style["hover_color"],
            text_color=style["text_color"],
            font=("Helvetica", 15, "bold"),
            border_color=style["border_color"],
            border_width=style["border_width"],
            **kwargs
        )

        # self.pack(pady=(30, 10))

    def _get_style(self, type: str):
        if type == "white":
            return {
                "fg_color": "#ffffff",
                "hover_color": "#f0f0f0",
                "text_color": "#333333",
                "border_color": "#cccccc",
                "border_width": 1,
            }
        else:  # default: primary
            return {
                "fg_color": "#5670f6",
                "hover_color": "#3450f0",
                "text_color": "#ffffff",
                "border_color": "#3450f0",
                "border_width": 1,
            }

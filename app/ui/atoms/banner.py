import customtkinter as ctk

class Banner(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#5670f6", height=80, corner_radius = 0, **kwargs) 
        self.pack(fill="x")

        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.pack(padx=20, pady=20, anchor="w")

        # title - EncTalk
        title = ctk.CTkLabel(
            text_frame,
            text="EncTalk",
            font=("Helvetica", 22, "bold", "italic"),
            text_color="white"
        )
        title.pack(side="left")

        # subtitle - The Fast and Secure Chat
        subtitle = ctk.CTkLabel(
            text_frame,
            text="The Fast and Secure Chat",
            font=("Helvetica", 14),
            text_color="white"
        )
        subtitle.pack(side="left", padx=15, pady=(3, 0))

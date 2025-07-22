import customtkinter as ctk

class Toast(ctk.CTkToplevel):
    def __init__(self, master, message: str, type: str = "info", duration: int = 2000):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="#5670f6")

        # frame
        frame = ctk.CTkFrame(self, corner_radius=12, fg_color="white")
        frame.pack(padx=10, pady=10, expand=True, fill="both")  # 패딩 추가!
        frame.columnconfigure(1, weight=1)

        # icon map
        icon_map = {
            "success": ("#00C851", "✔"),
            "error": ("#ff4444", "✖"),
            "info": ("#33b5e5", "ℹ"),
        }
        color, icon = icon_map.get(type, icon_map["info"])

        # icon
        icon_label = ctk.CTkLabel(frame, text=icon, text_color=color,
                                  font=("Arial", 18), width=32)
        icon_label.grid(row=0, column=0, padx=(16, 8), pady=12)

        # message
        message_label = ctk.CTkLabel(frame, text=message, font=("Helvetica", 13),
                                     text_color="black", anchor="w", justify="left")
        message_label.grid(row=0, column=1, sticky="w", padx=(0, 16), pady=12)

        # let it layout before positioning
        self.update_idletasks()

        # width, height 계산 후 중앙 상단 위치
        w = self.winfo_width()
        h = self.winfo_height()
        root_x = master.winfo_rootx()
        root_y = master.winfo_rooty()
        root_w = master.winfo_width()
        x = root_x + (root_w // 2) - (w // 2)
        y = root_y + 40
        self.geometry(f"+{x}+{y}")

        self.after(duration, self.destroy)

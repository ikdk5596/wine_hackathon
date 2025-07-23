import customtkinter as ctk

class Toast(ctk.CTkToplevel):
    def __init__(self, master, message: str, type: str = "info", duration: int = 2000):
        # super().__init__(None)
        super().__init__(master)
        self.overrideredirect(True)
        self.transient(master)      
        self.lift(master)        
        self.attributes("-topmost", False)  

        # frame
        frame = ctk.CTkFrame(self, fg_color="white")
        frame.pack(expand=True, fill="both", padx=2, pady=2)
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
        icon_label.grid(row=0, column=0, padx=(8, 8), pady=12)

        # message
        message_label = ctk.CTkLabel(frame, text=message, font=("Helvetica", 13),
                                     text_color="black", anchor="w", justify="left")
        message_label.grid(row=0, column=1, sticky="w", padx=(0, 16), pady=12)

        # let it layout before positioning
        self.update_idletasks()

        # position the toast - center top
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        root_x = master.winfo_rootx()
        root_y = master.winfo_rooty()
        root_w = master.winfo_width()
        x = root_x + (root_w // 2) - (w // 2)
        y = root_y + 40 
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.after(duration, self.destroy)

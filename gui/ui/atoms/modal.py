import customtkinter as ctk

class Modal(ctk.CTkToplevel):
    def __init__(self, master, child_widget_class, **child_kwargs):
        super().__init__(master)
        self.title("")
        self.geometry("400x300")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="gray85")  # 테두리 그림자 효과

        # 중앙 정렬
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() // 2) - 200
        y = master.winfo_rooty() + (master.winfo_height() // 2) - 150
        self.geometry(f"+{x}+{y}")

        # 내부 Frame
        self.container = ctk.CTkFrame(self, corner_radius=12, fg_color="white")
        self.container.pack(expand=True, fill="both", padx=2, pady=2)

        # 자식 위젯 삽입
        self.child = child_widget_class(self.container, **child_kwargs)
        self.child.pack(expand=True, fill="both", padx=20, pady=20)

        # 닫기 버튼
        close_button = ctk.CTkButton(self.container, text="Close", command=self.destroy, width=80)
        close_button.pack(pady=(0, 10))

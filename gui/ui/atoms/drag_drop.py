import customtkinter as ctk
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

class DragDrop(ctk.CTkFrame):
    def __init__(self, master, on_drop, **kwargs):
        super().__init__(master, fg_color="#f4f4f4", corner_radius=8, **kwargs)
        self.on_drop = on_drop

        self.file_path = None

        # 라벨: 초기 메시지
        self.label = ctk.CTkLabel(self, text="Drag and drop", text_color="#777777")
        self.label.pack(expand=True, fill="both", padx=10, pady=10)

        # TkinterDnD 등록
        self.register_drop_target()

    def register_drop_target(self):
        # self._root()는 Tk나 CTk의 인스턴스를 반환
        # 그 위에 drop_target_register 를 호출해야 드래그 인식됨
        root = self._root()
        if not isinstance(root, TkinterDnD.Tk):
            raise RuntimeError("Root window must be a TkinterDnD.Tk instance")

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._on_file_drop)

    def _on_file_drop(self, event):
        # 파일 경로 추출
        path = event.data.strip().strip("{}")  # 윈도우에선 {경로} 형태일 수 있음
        self.file_path = path
        self.label.configure(text=f"Dropped:\n{path}", text_color="#444444")

        # 콜백 함수 호출
        if callable(self.on_drop):
            self.on_drop(path)


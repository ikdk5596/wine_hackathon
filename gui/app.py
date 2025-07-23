import customtkinter as ctk
from ui.pages.login_page import LoginPage

APP_TITLE = "EncTalk"
WINDOW_SIZE = "502x874"
MIN_WINDOW_SIZE = (402, 874)
THEME = "blue"
MODE = "system"

def configure_ctk():
    ctk.set_appearance_mode(MODE)
    ctk.set_default_color_theme(THEME)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._init_pages()

    def _setup_window(self):
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(*MIN_WINDOW_SIZE)

    def _init_pages(self):
        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True, fill="both")

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        from ui.pages.login_page import LoginPage
        from ui.pages.signup_page import SignupPage
        from ui.pages.main_page import MainPage

        self.frames = {}
        for PageClass in (LoginPage, SignupPage, MainPage):
            name = PageClass.__name__
            frame = PageClass(self.container, controller=self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[name] = frame

        self.show_frame("LoginPage")

    def show_frame(self, page_class):
        frame = self.frames.get(page_class)
        if frame is None:
            raise ValueError(f"Page {page_class} not found in frames.")
        else:
            frame.tkraise()
            frame.reset()

if __name__ == "__main__":
    configure_ctk()
    app = App()
    app.mainloop()

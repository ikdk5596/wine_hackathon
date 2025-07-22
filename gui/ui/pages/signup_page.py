import customtkinter as ctk
from ui.components.input import Input
from ui.components.button import Button
from ui.components.link import Link
from ui.components.toast import Toast
from utils.api import users

class SignupPage(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="#5670f6", **kwargs)
        self.controller = controller

        # center align frame
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # title
        title = ctk.CTkLabel(
            self.center_frame,
            text="EncTalk",
            font=("Helvetica", 32, "bold", "italic"),
            text_color="white"
        )
        title.pack(pady=(0, 40))

        # input - ID
        self.id_input = Input(
            master=self.center_frame,
            placeholder="ID",
            width=300
        )

        # input - Password
        self.pw_input = Input(
            master=self.center_frame,
            placeholder="Password",
            width=300
        )

        # button - Sign Up
        self.login_button = Button(
            master=self.center_frame,
            text="Sign Up",
            type="white",
            command=self.handle_signup
        )

        # link - Login
        self.signup_link = Link(
            master=self.center_frame,
            text="or Login",
            command=self.handle_login
        )

    def handle_signup(self):
        user_id = self.id_input.get()
        password = self.pw_input.get()

        if users.register_user(user_id, password):
            Toast(self, "회원가입 성공!", type="success", duration=2000)
        else:
            Toast(self, "이미 존재하는 사용자입니다.", type="error", duration=2000)

    def handle_login(self):
        self.controller.show_frame("LoginPage")


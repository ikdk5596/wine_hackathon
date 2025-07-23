import customtkinter as ctk
from ui.atoms.input import Input
from ui.atoms.button import Button
from ui.atoms.link import Link
from ui.atoms.toast import Toast
from states.user_store import UserStore
from controllers.user_controller import UserController

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
        self.id_input.pack(pady=(0, 10))

        # input - Password
        self.pw_input = Input(
            master=self.center_frame,
            placeholder="Password",
            show="*",
            width=300
        )
        self.pw_input.pack(pady=(0, 20))

        # button - Sign Up
        self.login_button = Button(
            master=self.center_frame,
            text="Sign Up",
            type="white",
            command=self.handle_signup
        )
        self.login_button.pack(pady=(0, 10))

        # link - Login
        self.signup_link = Link(
            master=self.center_frame,
            text="or Login",
            command=self.handle_login
        )
        self.signup_link.pack()

    def handle_signup(self):
        user_id = self.id_input.get()
        password = self.pw_input.get()

        try:
            result = UserController().sign_up(user_id, password)
            if result['status'] == 'success':
                Toast(self, result['message'], type="success", duration=2000)
                self.controller.show_frame("LoginPage")
            else:
                Toast(self, result['message'], type="error", duration=2000)
        except Exception as e:
            Toast(self, f"Error: {str(e)}", type="error", duration=2000)

    def handle_login(self):
        self.controller.show_frame("LoginPage")


import customtkinter as ctk
from states.friends_store import FriendsStore, Friend
from ui.atoms.modal import Modal
from ui.atoms.button import Button
from ui.atoms.profile import Profile
from ui.organisms.add_friend import AddFriend
from controllers.friend_controller import FriendController

class FriendItem(ctk.CTkFrame):
    def __init__(self, master, friend: Friend, **kwargs):
        super().__init__(master, height=60, fg_color="transparent", **kwargs)
        self.configure(cursor="hand2")
        self.friend = friend

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.profile = Profile(self, image=friend.profile_image, size=62)
        self.profile.grid(row=0, column=0, rowspan=2, padx=(10, 20), pady=(10, 10))

        self.name_label = ctk.CTkLabel(self, text=friend.friend_id, font=("Helvetica", 13, "bold"), anchor="w")
        self.name_label.grid(row=0, column=1, sticky="w", pady=(8, 0))

        self.message_label = ctk.CTkLabel(self, text='', font=("Helvetica", 11), anchor="w")
        self.message_label.grid(row=1, column=1, sticky="w")

        # self.dot = ctk.CTkLabel(self, text="⬤", text_color="red", font=("Arial", 8))
        # self.dot.grid(row=0, column=2, padx=10, sticky="e")
        # self.dot.grid_remove()

        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._off_hover)

        friend.add_observer("profile_image", self._on_profile_image_change)
        # friend.add_observer("messages", self.update_profile)

    def _on_hover(self, event):
        self.configure(fg_color="#f5f5f5")

    def _off_hover(self, event):
        self.configure(fg_color="transparent")

    def _on_profile_image_change(self):
        self.profile.update_image(self.friend.profile_image)

    def update_message(self, message):
        self.message_label.configure(text=message)
        self.dot.grid()  # 빨간 점 표시
        self.unread = True


class FriendsList(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(10, 5))

        title = ctk.CTkLabel(title_frame, text="Friends", font=("Helvetica", 14), text_color="gray")
        title.pack(side="left")

        self.add_button = Button(title_frame, type="primary", text="+", width=12, height=12, command=self.open_modal)
        self.add_button.pack(side="right")

        self.items_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.items_frame.pack(fill="both", expand=True)

        FriendsStore().add_observer("friends_list", self._on_friends_list_change)

    def open_modal(self):
        # def my_modal_content(master):
        #     return ctk.CTkLabel(master, text="이것은 모달입니다!")

        Modal(self, AddFriend)

    def delete_friend(self, user_id):
        FriendController().delete_friend(user_id)

    def _on_friends_list_change(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        for friend in FriendsStore().friends_list:
            item = FriendItem(self.items_frame, friend)
            item.pack(fill="x", padx=10)
            # item.bind("<Button-1>", lambda e, user_id=friend["user_id"]: self.controller.open_chat(user_id))


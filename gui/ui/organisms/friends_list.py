import customtkinter as ctk
from ui.atoms.modal import Modal
from ui.atoms.button import Button
from ui.atoms.profile import Profile
from ui.organisms.add_friend import AddFriend
from states.friends_store import FriendsStore, Friend
from controllers.friend_controller import FriendController

class FriendItem(ctk.CTkFrame):
    def __init__(self, master, controller, friend: Friend, **kwargs):
        super().__init__(master, height=60, fg_color="transparent", **kwargs)
        self.controller = controller
        self.configure(cursor="hand2")
        self.friend = friend

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.profile = Profile(self, image=friend.profile_image, size=60)
        self.profile.grid(row=0, column=0, rowspan=2, padx=(10, 20), pady=(15, 15))

        self.name_label = ctk.CTkLabel(self, text=friend.friend_id, font=("Helvetica", 14, "bold"), anchor="w")
        self.name_label.grid(row=0, column=1, sticky="ws", pady=(6, 0))

        last_message = friend.messages_list[-1] if friend.messages_list else None
        last_message = '사진' if not last_message or not last_message["text"] else last_message['text']
        self.message_label = ctk.CTkLabel(self, text=last_message, font=("Helvetica", 14), anchor="w")
        self.message_label.grid(row=1, column=1, sticky="nw", pady=(0, 10))

        unread_count = 0
        for message in friend.messages_list[::-1]:
            if not message["is_read"]:
                unread_count += 1
            else:
                break
        self.unread_count_label = ctk.CTkLabel(self, text=str(unread_count), font=("Helvetica", 12), text_color="white", fg_color="#cf4f4a", corner_radius=9, width=18, height=18)
        self.unread_count_label.grid(row=0, column=2, sticky="ne", padx=(0, 10), pady=(8, 0))
        if unread_count == 0:
            self.unread_count_label.grid_remove()

        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._off_hover)
        self.bind("<Button-1>", self._on_click)

        friend.add_observer("profile_image", self._on_profile_image_change)
        friend.add_observer("messages_list", self._on_messages_list_change)

    def _on_hover(self, event):
        self.configure(fg_color="#f5f5f5")

    def _off_hover(self, event):
        self.configure(fg_color="transparent")

    def _on_click(self, event):
        FriendController().select_friend(self.friend.friend_id)
        self.controller.show_frame("ChatPage")

    def _on_profile_image_change(self):
        self.profile.update_image(self.friend.profile_image)

    def _on_messages_list_change(self):
        if self.friend.messages_list:
            last_message = self.friend.messages_list[-1]
            last_message = '사진' if not last_message["text"] else last_message['text']
            self.message_label.configure(text=last_message)

            unread_count = 0
            for message in self.friend.messages_list[::-1]:
                if not message["is_read"]:
                    unread_count += 1
                else:
                    break
            self.unread_count_label.configure(text=str(unread_count))
            if unread_count == 0:
                self.unread_count_label.grid_remove()
            else:
                self.unread_count_label.grid()
        else:
            self.message_label.configure(text="")


class FriendsList(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller

        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(10, 5))

        title = ctk.CTkLabel(title_frame, text="Friends", font=("Helvetica", 14), text_color="gray")
        title.pack(side="left")

        self.add_button = Button(title_frame, type="white", text="+", width=12, height=12, command=self._on_click_plus_button)
        self.add_button.pack(side="right")

        self.items_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.items_frame.pack(fill="both", expand=True)

        FriendsStore().add_observer("friends_list", self._on_friends_list_change)

    def _on_click_plus_button(self):
        Modal(self, lambda *args, **kwargs: AddFriend(*args, controller=self.controller, **kwargs))

    def _on_friends_list_change(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        for friend in FriendsStore().friends_list:
            item = FriendItem(self.items_frame, self.controller, friend)
            item.pack(fill="x", padx=10)



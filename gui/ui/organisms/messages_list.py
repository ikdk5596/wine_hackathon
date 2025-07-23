import customtkinter as ctk
from PIL import Image
from states.friends_store import FriendsStore
from states.user_store import UserStore
from ui.atoms.profile import Profile

class FriendMessage(ctk.CTkFrame):
    def __init__(self, master, text, friend_id: str, profile_image: Image.Image | None, show_profile: bool):
        super().__init__(master, fg_color="transparent")
        self.columnconfigure(1, weight=1)

        # Show profile image and name if specified
        if show_profile:
            img_label = Profile(self, image=profile_image, size=60)
            img_label.grid(row=0, column=0, rowspan=2, padx=(5, 10), pady=5, sticky="nw")

            name_label = ctk.CTkLabel(self, text=friend_id, font=ctk.CTkFont(weight="bold"), text_color="black")
            name_label.grid(row=0, column=1, sticky="nw", padx=(0, 0), pady=(5, 0))

        msg_label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=13),
            text_color="black",
            fg_color="white",
            corner_radius=6,
            height=30
        )

        msg_label.grid(
            row=1 if show_profile else 0,
            column=1,
            sticky="w",
            pady= 0,
            padx=(2, 2) if show_profile else (74, 2),
        )


class MyMessage(ctk.CTkFrame):
    def __init__(self, master, text):
        super().__init__(master, fg_color="transparent")
        msg_label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=13),
            text_color="white",
            fg_color="#3366cc",
            corner_radius=6,
            height=30,
            justify="left",
            anchor="w",
            wraplength=250,
            padx=10,
            pady=6
        )
        msg_label.pack(anchor="e", padx=0, pady=0)


class MessagesList(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent", corner_radius=0)

        self.selected_friend = FriendsStore().selected_friend
        prev_sender = None 
        if self.selected_friend:
            for msg in FriendsStore().selected_friend.messages_list:
                sender = msg["sender_id"]
                show_profile = sender != "Me" and sender != prev_sender 

                if sender == UserStore().user_i:
                    item = MyMessage(self, msg["text"])
                else:
                    item = FriendMessage(
                        self,
                        msg["text"],
                        self.selected_friend.friend_id,
                        self.selected_friend.profile_image,
                        show_profile
                    )
                item.pack(fill="x", anchor="w", pady=2, padx=5)
                prev_sender = sender

        FriendsStore().add_observer("selected_friend", self._on_selected_friend_change)

    def _on_messages_list_change(self):
        for widget in self.winfo_children():
            widget.destroy()

        prev_sender = None
        if self.selected_friend:
            for msg in self.selected_friend.messages_list:
                sender = msg["sender_id"]
                show_profile = sender != UserStore().user_id and sender != prev_sender 

                if sender == UserStore().user_id:
                    item = MyMessage(self, msg["text"])
                else:
                    item = FriendMessage(
                        self,
                        msg["text"],
                        self.selected_friend.friend_id,
                        self.selected_friend.profile_image,
                        show_profile
                    )
                item.pack(fill="x", anchor="w", pady=1, padx=5)
                prev_sender = sender

    def _on_selected_friend_change(self):
        if self.selected_friend != FriendsStore().selected_friend:
            if self.selected_friend:
                self.selected_friend.remove_observer("messages_list", self._on_messages_list_change)
            if FriendsStore().selected_friend:
                FriendsStore().selected_friend.add_observer("messages_list", self._on_messages_list_change)
            self.selected_friend = FriendsStore().selected_friend

        self._on_messages_list_change()

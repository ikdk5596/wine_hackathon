import customtkinter as ctk
from PIL import Image
from states.friends_store import FriendsStore
from states.user_store import UserStore
from ui.atoms.profile import Profile
from ui.atoms.modal import Modal
from utils.core.encoding import visualize_latent
from ui.organisms.decrypt_image import DecryptImage

class FriendMessage(ctk.CTkFrame):
    def __init__(self, master, message, friend_id: str, profile_image: Image.Image | None, show_profile: bool):
        super().__init__(master, fg_color="transparent")
        self.columnconfigure(1, weight=1)
        self.message = message

        # Show profile image and name if specified
        if show_profile:
            img_label = Profile(self, image=profile_image, size=60)
            img_label.grid(row=0, column=0, rowspan=2, padx=(5, 10), pady=5, sticky="nw")

            name_label = ctk.CTkLabel(self, text=friend_id, font=ctk.CTkFont(weight="bold"), text_color="black")
            name_label.grid(row=0, column=1, sticky="nw", padx=(0, 0), pady=(5, 0))

        message_frame = ctk.CTkFrame(self, fg_color="transparent")
        message_frame.grid(row=1 if show_profile else 0, column=1, sticky="w", padx=(0, 2) if show_profile else (74, 2), pady=(5, 0))

        if message["latent_tensor"] is not None:
            latent_tensor = message["latent_tensor"]
            latent_image = visualize_latent(latent_tensor)
            tk_image = ctk.CTkImage(dark_image=latent_image, size=(64, 64))
            latent_image_label = ctk.CTkLabel(message_frame, image=tk_image, text="")
            latent_image_label.pack(anchor="w", padx=0, pady=0)
            latent_image_label.bind("<Button-1>", self._on_click_image)
            
        if message["text"]:
            msg_label = ctk.CTkLabel(
                message_frame,
                text=message["text"],
                font=ctk.CTkFont(size=13),
                text_color="black",
                fg_color="white",
                corner_radius=6,
                height=30
            )
            msg_label.pack(anchor="w", padx=0, pady=0)

    def _on_click_image(self, event):
        def show_decrypt_image(*args, **kwargs):
            return DecryptImage(*args, message=self.message, **kwargs)

        Modal(self, show_decrypt_image, height=500)


class MyMessage(ctk.CTkFrame):
    def __init__(self, master, message):
        super().__init__(master, fg_color="transparent")

        if message["latent_tensor"] is not None:
            latent_tensor = message["latent_tensor"]
            latent_image = visualize_latent(latent_tensor)
            tk_image = ctk.CTkImage(dark_image=latent_image, size=(64, 64))
            latent_image_label = ctk.CTkLabel(self, image=tk_image, text="")
            latent_image_label.pack(anchor="e", padx=0, pady=0)
            
        if message["text"]:
            msg_label = ctk.CTkLabel(
                self,
                text=message["text"],
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
            for message in FriendsStore().selected_friend.messages_list:
                sender = message["sender_id"]
                show_profile = sender != UserStore().user_id and sender != prev_sender

                if sender == UserStore().user_i:
                    item = MyMessage(self, message)
                else:
                    item = FriendMessage(
                        self,
                        message,
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
            for message in self.selected_friend.messages_list:
                sender = message["sender_id"]
                show_profile = sender != UserStore().user_id and sender != prev_sender

                if sender == UserStore().user_id:
                    item = MyMessage(self, message)
                else:
                    item = FriendMessage(
                        self,
                        message,
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

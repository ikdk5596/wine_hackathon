import customtkinter as ctk
from PIL import Image
from states.friends_store import FriendsStore
from states.user_store import UserStore
from ui.atoms.profile import Profile
from ui.atoms.modal import Modal
from ui.atoms.image_frame import ImageFrame
from utils.image import latent_to_gray_image
from utils.core.encoding import decode_latent_to_image
from ui.organisms.decrypt_image import DecryptImage
from utils.core.encryption import decrypt_latent

class FriendMessage(ctk.CTkFrame):
    def __init__(self, master, message, friend_id: str, profile_image: Image.Image | None, show_profile: bool):
        super().__init__(master, fg_color="transparent")
        self.columnconfigure(1, weight=1)
        self.message = message

        # Show profile image and name
        if show_profile:
            img_label = Profile(self, image=profile_image, size=60)
            img_label.grid(row=0, column=0, rowspan=2, padx=(5, 10), pady=5, sticky="nw")

            name_label = ctk.CTkLabel(self, text=friend_id, font=ctk.CTkFont(weight="bold"), text_color="black")
            name_label.grid(row=0, column=1, sticky="nw", padx=(2, 0), pady=(7, 0))

        # Show message content
        message_frame = ctk.CTkFrame(self, fg_color="transparent")
        message_frame.grid(row=1 if show_profile else 0, column=1, sticky="w", padx=(0, 2) if show_profile else (74, 2), pady=(5, 0))

        if message["enc_latent_tensor"] is not None:
            latent_image = latent_to_gray_image(message["enc_latent_tensor"])
            self.latent_image_frame = ImageFrame(
                master=message_frame,
                image=latent_image,
                width=128,
                height=128,
                border_radius=5
            )
            self.latent_image_frame.pack(anchor="w", padx=0, pady=0)
            self.latent_image_frame.bind("<Button-1>", self._on_click_image)

        if message["text"]:
            msg_label = ctk.CTkLabel(
                message_frame,
                text=message["text"],
                font=ctk.CTkFont(size=15),
                text_color="black",
                fg_color="white",
                corner_radius=6,
                height=30
            )
            msg_label.pack(anchor="w", padx=0, pady=0)

    def _on_click_image(self, event):
        Modal(self, lambda *args, **kwargs: DecryptImage(*args, message=self.message, **kwargs))


class MyMessage(ctk.CTkFrame):
    def __init__(self, master, message):
        super().__init__(master, fg_color="transparent")
        if message["enc_latent_tensor"] is not None:
            latent_tensor = decrypt_latent(message["enc_latent_tensor"], message["seed_string"])
            latent_image = decode_latent_to_image(latent_tensor)
            self.latent_image_frame = ImageFrame(
                master=self,
                image=latent_image,
                width=128,
                height=128,
                border_radius=5
            )
            self.latent_image_frame.pack(anchor="e", padx=0, pady=0)
            
        if message["text"]:
            msg_label = ctk.CTkLabel(
                self,
                text=message["text"],
                font=ctk.CTkFont(size=15),
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

        userStore = UserStore()
        friendStore = FriendsStore()
        self.selected_friend = friendStore.selected_friend

        self.rendered_count = 0

        prev_sender = None 
        if self.selected_friend:
            for message in friendStore.selected_friend.messages_list:
                sender = message["sender_id"]
                show_profile = sender != userStore.user_id and sender != prev_sender

                if sender == userStore.user_id:
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
                self.rendered_count += 1

        FriendsStore().add_observer("selected_friend", self._on_selected_friend_change)

    def _on_messages_list_change(self):
        if not self.selected_friend:
            return

        messages = self.selected_friend.messages_list
        new_messages = messages[self.rendered_count:]

        prev_sender = messages[self.rendered_count - 1]["sender_id"] if self.rendered_count > 0 else None
        for message in new_messages:
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
            self.rendered_count += 1

        # Scroll to the bottom
        self.after(0, lambda: self._parent_canvas.yview_moveto(1.0))

    def _on_selected_friend_change(self):
        new_friend = FriendsStore().selected_friend

        # Replace the observer
        if self.selected_friend != new_friend:
            if self.selected_friend:
                self.selected_friend.remove_observer("messages_list", self._on_messages_list_change)
            if new_friend:
                new_friend.add_observer("messages_list", self._on_messages_list_change)
            self.selected_friend = new_friend

        # Update messages
        for widget in self.winfo_children():
            widget.destroy()
        self.rendered_count = 0 
        self._on_messages_list_change()

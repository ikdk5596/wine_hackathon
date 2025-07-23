import customtkinter as ctk

class FriendItem(ctk.CTkFrame):
    def __init__(self, master, user_id, profile_image, name, message="", **kwargs):
        super().__init__(master, height=60, fg_color="transparent", **kwargs)
        self.user_id = user_id
        self.name = name
        self.message = message
        self.profile_image = profile_image
        self.unread = False

        self.configure(cursor="hand2")

        self.grid_columnconfigure(1, weight=1)

        self.image_label = ctk.CTkLabel(self, image=self.profile_image, text="")
        self.image_label.grid(row=0, column=0, rowspan=2, padx=(10, 10), pady=5)

        self.name_label = ctk.CTkLabel(self, text=name, font=("Helvetica", 13, "bold"), anchor="w")
        self.name_label.grid(row=0, column=1, sticky="w", pady=(8, 0))

        self.message_label = ctk.CTkLabel(self, text=message, font=("Helvetica", 11), anchor="w")
        self.message_label.grid(row=1, column=1, sticky="w")

        self.dot = ctk.CTkLabel(self, text="⬤", text_color="red", font=("Arial", 8))
        self.dot.grid(row=0, column=2, padx=10, sticky="e")
        self.dot.grid_remove()

        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._off_hover)

    def _on_hover(self, event):
        self.configure(fg_color="#f5f5f5")

    def _off_hover(self, event):
        self.configure(fg_color="transparent")

    def update_profile(self, new_name, new_profile_img):
        self.name_label.configure(text=new_name)
        self.image_label.configure(image=new_profile_img)

    def update_message(self, message):
        self.message_label.configure(text=message)
        self.dot.grid()  # 빨간 점 표시
        self.unread = True

    def mark_as_read(self):
        self.dot.grid_remove()
        self.unread = False


class FriendsList(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(10, 5))

        title = ctk.CTkLabel(title_frame, text="Friends", font=("Helvetica", 14), text_color="gray")
        title.pack(side="left")

        self.add_button = ctk.CTkButton(title_frame, text="+", width=28, height=28, command=self.add_friend)
        self.add_button.pack(side="right")

        self.items_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.items_frame.pack(fill="both", expand=True)

        self.friend_items = {}  # user_id -> FriendItem

    def add_friend(self, user_id=None, name="", message="", profile_image=None):
        if user_id in self.friend_items:
            return  # 중복 추가 방지

        item = FriendItem(self.items_frame, user_id, profile_image, name, message)
        self.friend_items[user_id] = item
        item.pack(fill="x")

    def delete_friend(self, user_id):
        if user_id in self.friend_items:
            self.friend_items[user_id].destroy()
            del self.friend_items[user_id]

    def update_friend(self, user_id, update_type="message", **kwargs):
        item = self.friend_items.get(user_id)
        if not item:
            return

        if update_type == "profile":
            item.update_profile(kwargs.get("name", item.name), kwargs.get("profile_image", item.profile_image))
        elif update_type == "message":
            item.update_message(kwargs.get("message", item.message))
            item.pack_forget()
            item.pack(fill="x", before=list(self.friend_items.values())[0])

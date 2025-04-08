from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

class WelcomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Welcome to DriveClonr", font=("Helvetica", 20, "bold")).pack(pady=20)
        ttk.Label(self, text="Clone your Google Drive effortlessly", font=("Helvetica", 12, "italic")).pack(pady=10)

        # Load and resize the logo
        image = Image.open("assets/logo.png")
        image = image.resize((200, 200), Image.LANCZOS)  # Resize to 200x200 with high-quality downsampling
        self.logo = ImageTk.PhotoImage(image)

        ttk.Label(self, image=self.logo).pack(pady=20)

        ttk.Button(self, text="Start ➡️", command=self.controller.show_login).pack(pady=30)

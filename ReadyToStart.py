import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
from DriveDownloadr import DriveDownloadr
class ReadyToStart(tk.Frame):
    def __init__(self, parent: tk.Tk, service, config: dict):
        super().__init__(parent)
        self.parent = parent
        self.service = service
        self.config = config
        # LOGO IMAGE
        self.logo_image = Image.open("DriveClonr Logo.png")
        self.logo_image = self.logo_image.resize((200, 200)) 
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(self, image=self.logo_photo)
        self.logo_label.pack()

        # WELCOME TEXT
        self.welcome_text = ttk.Label(self, text="Ready to Start?", font=("Helvetica", 16, "bold"))
        self.welcome_text.pack(pady=5)

        self.start_button = ttk.Button(self, text="Start Cloning!", command=self.start_cloning)
        self.start_button.pack(pady=5)
        self.pack()
    
    def start_cloning(self):
        super().destroy()
        DriveDownloadr(self.parent, self.service, self.config).pack()        
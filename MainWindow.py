"""
MainWindow.py
This file contains the classes required to create the main window of the application
"""

import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
from EULAScreen import EULAView
import os

class MainWindow():
    """
    Class for the main window of the application
    """
    def __init__(self, parent: tk.Tk) -> None:
        self.parent = parent
        self.current_frame = ttk.Frame(self.parent, padding="5")
        
        # Experimental Dark Mode - Enable at your own risk
        
        # self.parent.tk_setPalette(background="#333333", foreground="#FFFFFF")
        # style = ttk.Style()
        # style.theme_use('clam')

        # # Configure colors for specific widgets
        # style.configure("TLabel", foreground="#FFFFFF", background="#333333")
        # style.configure("TButton", foreground="#FFFFFF", background="#555555")
        # style.configure("TEntry", foreground="#FFFFFF", background="#444444")
        # style.configure("TFrame", foreground="#FFFFFF", background="#333333")
        # style.configure("TCheckbutton", foreground="#FFFFFF", background="#333333")
        # style.configure("TRadiobutton", foreground="#FFFFFF", background="#333333")
        # style.configure("TLabelFrame", foreground="#FFFFFF", background="#444444")
        # LOGO IMAGE
        self.logo_image = Image.open("DriveClonr Logo.png")
        self.logo_image = self.logo_image.resize((200, 200)) 
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(self.current_frame, image=self.logo_photo)
        self.logo_label.pack()

        # WELCOME TEXT
        self.welcome_text = ttk.Label(self.current_frame, text="Welcome To DriveClonr", font=("Helvetica", 16, "bold"))
        self.welcome_text.pack(pady=5)
        self.tagline = ttk.Label(self.current_frame, text="The BEST way to clone your Google Drive!", font=("Helvetica", 12, "italic"), wraplength=300, justify="center")
        self.tagline.pack(pady=5)
        
        # START BUTTON
        self.start_button = ttk.Button(self.current_frame, text="Start Cloning!", command=lambda: self.transition(EULAView(self.parent)))
        self.start_button.pack()
        
        self.current_frame.pack()

        # WINDOW ICON
        self.parent.iconbitmap("DriveClonr Logo.ico")

        # WINDOW SIZE
        self.parent.geometry("350x350")
        self.parent.resizable(False, False)
        self.parent.title("DriveClonr 2023.7")
        
        # if a file called creds.json is not found in the same directory as the program, then the program will not run
        if not os.path.exists("creds.json"):
            tk.messagebox.showerror("Error", "creds.json not found. Please download it from the Google Cloud Console and place it in the same directory as this program.")
            self.parent.destroy()
            exit()
        
    def transition(self, frame: ttk.Frame) -> None:
        """
        Transition to a new frame
        """
        self.current_frame.pack_forget()
        self.current_frame = frame
        self.current_frame.pack()

if __name__ == "__main__":
    root = tk.Tk()
    x = MainWindow(root)
    x.parent.mainloop()

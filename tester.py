import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
from EULAScreen import EULAView

class MainWindow():
    """
    Class for the main window of the application
    """
    def __init__(self, parent: tk.Tk) -> None:
        self.parent = parent
        self.current_frame = ttk.Frame(self.parent, padding="20")

        # LOGO IMAGE
        self.logo_image = Image.open("DriveClonr Logo.png")
        self.logo_image = self.logo_image.resize((200, 200)) 
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(self.current_frame, image=self.logo_photo, background="#F0F0F0")
        self.logo_label.pack()

        # WELCOME TEXT
        self.welcome_text = ttk.Label(self.current_frame, text="Welcome To DriveClonr", font=("Helvetica", 16, "bold"), background="#F0F0F0")
        self.welcome_text.pack(pady=10)
        self.tagline = ttk.Label(self.current_frame, text="The industry standard for Google Drive cloning", font=("Helvetica", 12, "italic"), wraplength=300, justify="center", background="#F0F0F0")
        self.tagline.pack(pady=10)
        
        # START BUTTON
        self.start_button = ttk.Button(self.current_frame, text="Start Cloning!", command=lambda: self.transition(EULAView(self.parent)))
        self.start_button.pack(pady=10)
        
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        # WINDOW ICON
        self.parent.iconbitmap("DriveClonr Logo.ico")

        # WINDOW SIZE AND APPEARANCE
        self.parent.geometry("400x400")
        self.parent.title("DriveClonr 2023.7")
        self.parent.configure(background="#F0F0F0")
        
    def transition(self, frame: ttk.Frame) -> None:
        """
        Transition to a new frame
        """
        self.current_frame.pack_forget()
        self.current_frame = frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    x = MainWindow(root)
    x.parent.mainloop()

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
from AccountSelectorScreen import AccountSelector

class EULAView(tk.Frame):
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent)
        self.parent = parent
        legal_text = ttk.Label(self, text="But first, the legal stuff...", font=("Helvetica", 16, "bold"))
        legal_text.pack()
        eula_text = ScrolledText(self, wrap=tk.WORD)
        eula_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        with open("EULA.txt") as f:
            eula_text.insert("1.0", f.read())

        # Accept and Decline buttons
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack()

        accept_button = ttk.Button(buttons_frame, text="I Accept", command=lambda: self.destroy())
        accept_button.pack(side="left", padx=5, pady=2)

        decline_button = ttk.Button(buttons_frame, text="I Decline", command=self.parent.destroy)
        decline_button.pack(side="left", padx=5, pady=2)
        accept_text = ttk.Label(self, text="By clicking \"I Accept\", you agree to the terms of the EULA and agree to abide by them.", font=("Helvetica", 12, "italic"))
        accept_text.pack()
        
        window_width = 700
        window_height = 500

        # Screen dimensions
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        # Calculate the x and y coordinates for centering the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Set the geometry of the window to center it on the screen
        self.parent.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.pack()
    
    def destroy(self):
        super().destroy()
        AccountSelector(self.parent).pack()
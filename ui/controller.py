# ui/controller.py

import tkinter as tk
from ui.welcome_screen import WelcomeScreen
from ui.login_screen import LoginScreen
from ui.tree_screen import TreeSelectorScreen

class AppController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DriveClonr")
        self.geometry("700x600")
        self.resizable(False, False)

        self.service = None
        self.creds = None
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.show_welcome()

    def clear_screen(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_welcome(self):
        self.clear_screen()
        WelcomeScreen(self.container, self).pack(fill="both", expand=True)

    def show_login(self):
        self.clear_screen()
        LoginScreen(self.container, self).pack(fill="both", expand=True)

    def show_tree_selector(self, service):
        self.service = service
        self.clear_screen()
        TreeSelectorScreen(self.container, self, service).pack(fill="both", expand=True)
    
    def show_config_screen(self, service, config=None):
        self.service = service
        self.clear_screen()
        from ui.config_screen import ConfigScreen
        ConfigScreen(self.container, self, service).pack(fill="both", expand=True)


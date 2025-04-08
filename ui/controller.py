# ui/controller.py

import tkinter as tk
from core.model.clonr_config import ClonrConfig
from ui.drive_download_screen import DriveDownloadScreen
from ui.welcome_screen import WelcomeScreen
from ui.login_screen import LoginScreen
from ui.tree_screen import TreeSelectorScreen
from ui.config_screen import ConfigScreen

class AppController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DriveClonr")
        self.geometry("700x600")
        self.resizable(False, False)

        self.iconbitmap("assets/logo.ico")
        self.configure(bg="#f0f0f0")

        self.auth = None

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
        self.auth = service
        self.clear_screen()
        TreeSelectorScreen(self.container, self, service).pack(fill="both", expand=True)
    
    def show_config_screen(self, auth, config: ClonrConfig):
        self.clear_screen()
        ConfigScreen(self.container, self, auth, config).pack(fill="both", expand=True)


    def show_download_screen(self, service, config, log_file = open("download.log", "w")):
        self.clear_screen()
        DriveDownloadScreen(self.container, self, service, config, log_file).pack(fill="both", expand=True)
    
    def show_main_screen(self):
        self.clear_screen()
        TreeSelectorScreen(self.container, self, self.auth).pack(fill="both", expand=True)
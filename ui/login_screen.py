# ui/login_screen.py

import tkinter as tk
from tkinter import ttk
from core.auth import GoogleAuth
from core.constants import DISCOVERY_SERVICE_URL, SCOPES
# import .ui.controller

class LoginScreen(tk.Frame):

    # controller: controller.AppController

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Sign In to Your Google Account", font=("Helvetica", 16, "bold")).pack(pady=20)
        ttk.Button(self, text="Sign In with Google", command=self.sign_in).pack(pady=10)

        self.status = ttk.Label(self, text="", font=("Helvetica", 10))
        self.status.pack(pady=10)

    def sign_in(self):
        self.status.config(text="Authenticating... Please wait.")
        self.update()

        try:
            auth = GoogleAuth("assets/creds.json", SCOPES)
            creds = auth.authenticate()
            service = auth.build_service("drive", "v3", discovery_url=DISCOVERY_SERVICE_URL)
            self.controller.show_tree_selector(auth)
        except Exception as e:
            self.status.config(text=f"Login failed: {e}")

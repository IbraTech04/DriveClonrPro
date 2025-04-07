from __future__ import print_function

import tkinter as tk
import tkinter.ttk as ttk
from typing import TextIO
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from PIL import Image, ImageTk
from Config import ConfigWindow

SCOPES = ['https://www.googleapis.com/auth/drive']


class AccountSelector(ttk.Frame):
    log_file: TextIO
    parent: tk.Tk
    service: Resource
    def __init__(self, parent: tk.Tk, log_file: TextIO):
        super().__init__(parent)
        self.parent = parent
        self.log_file = log_file
        print("Entered AccountSelector", file=self.log_file)
        # Now we want to create a basic sign-in screen
        self.top_text = ttk.Label(self, text="Please sign in to your Google account to continue", font=("Helvetica", 16, "bold"))
        self.tagline_text = ttk.Label(self, text="Make sure to sign in with the account whose drive you want to clone", font=("Helvetica", 12, "italic"))
        self.top_text.pack(pady=5)
        self.tagline_text.pack(pady=5)
        
        self.logo_image = Image.open("DriveClonr Logo.png")
        self.logo_image = self.logo_image.resize((200, 200)) 
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(self, image=self.logo_photo)
        self.logo_label.pack()
        
        self.sign_in_button = ttk.Button(self, text="Sign In", command=self.sign_in)
        self.sign_in_button.pack(pady=5)

    def sign_in(self):
        """
        Method which triggers the OAuth flow for the user to sign in
        """
        print("Signing in...", file=self.log_file)
        flow = InstalledAppFlow.from_client_secrets_file(
                'creds.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # print(creds.__dict__, file=open("creds.json", "w"))
        if not creds.valid:
            fail_text = ttk.Label(self, text="Hmm, that didn't seem to work. Try again.", font=("Helvetica", 12, "bold"), foreground="red")
            fail_text.pack()
            return
        print("Signed in!", file=self.log_file)
        DISCOVERY_SERVICE_URL = 'https://www.googleapis.com/discovery/v1/apis/drive/v3/rest'
        self.service = build('drive', 'v3', credentials=creds, discoveryServiceUrl=DISCOVERY_SERVICE_URL)
        self.destroy()
        # Bring the root window back to the front
        self.parent.attributes('-topmost', 1)
        self.parent.attributes('-topmost', 0)
        ConfigWindow(self.parent, self.service, self.log_file).pack()
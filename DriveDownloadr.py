import os
from tkinter import messagebox
import traceback
from typing import TextIO
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import io
from PIL import Image, ImageTk
import tkinter as tk
import tkinter.ttk as ttk
from threading import Thread
import re
import requests
import time

MIMETYPE_EXTENSIONS = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx", 
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx", 
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx", 
    "application/pdf": ".pdf", 
    "image/jpeg": ".jpg", 
    "image/png": ".png", 
    "image/svg+xml": ".svg", 
    "application/vnd.oasis.opendocument.text": ".odt", 
    "application/vnd.oasis.opendocument.spreadsheet": ".ods", 
    "application/vnd.oasis.opendocument.presentation": ".odp"
}

class DriveDownloadr(tk.Frame):
    """
    Class which contains all the methods related to actually cloning the user's drive
    
    === Public Attributes ===
    service: The Google Drive API service object
    config: The config dict
    log_file: The log file
    failed_files: A list of files that failed to download
    mime_type_mapping: A dict that maps each MimeType to the corresponding export MimeType
    extensions: A dict that maps each MimeType to the corresponding file extension
    === Representation Invariants ===
    service is a valid Google Drive API service object with the correct scopes
    config is a valid config dict that contains all the required keys
    mime_type_mapping[x] = the valid extension pair for extension[x]
    """
    parent: tk.Tk
    service: Resource
    config: dict[any, any]
    log_file: TextIO
    
    def __init__(self, parent: tk.Tk, service: Resource, log_file: TextIO, config: dict) -> None:
        super().__init__(parent)
        self.service = service
        self.config = config
        self.log_file = log_file

        self.failed_files = []
        
        # We need to make a dict that maps each MimeType to the corresponding export MimeType
        # Example: {"application/vnd.google-apps.document": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
        self.mime_type_mapping = {
            config_setting: self.config['mime_types'][config_setting]
            for config_setting in self.config['mime_types']
        }
        # We also need to do the same thing for extensions
        self.extensions = {
            mime_type: MIMETYPE_EXTENSIONS[self.mime_type_mapping[mime_type]]
            for mime_type in self.mime_type_mapping
        }
        
        # Add jamboard to both as PDF - Since it's not directly changable in the Config screen
        self.mime_type_mapping['application/vnd.google-apps.jam'] = 'application/pdf'
        self.extensions['application/vnd.google-apps.jam'] = '.pdf'

        # Header Text:
        self.header_text = ttk.Label(self, text="Cloning your Google Drive", font=("Helvetica", 16, "bold"))
        num_stages = "two" if self.config["shared"] and self.config['my_drive'] else "one"
        current_stage = "Your Files" if self.config['my_drive'] else "Shared Files"
        self.stage = ttk.Label(self, text=f"Stage one of {num_stages}: Downloading {current_stage}", font=("Helvetica", 12, "normal"), justify="center")
        self.header_text.grid(row=0, column=0, columnspan=2, pady=5)
        self.stage.grid(row=1, column=0, columnspan=2, pady=5, sticky="nswe")
        # Logo Image
        self.logo_image = Image.open("DriveClonr Logo.png")
        self.logo_image = self.logo_image.resize((200, 200))
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(self, image=self.logo_photo, justify="center")
        self.logo_label.grid(row=2, column=0, columnspan=2, rowspan=2, padx=10, sticky="nswe")
        # Progress Bar
        self.pb = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='indeterminate',
            length=280
        )
        self.pb.start(10)
        self.pb.grid(row=5, column=0, rowspan=2, pady=10, padx=10)
        # Placeholder text
        self.current_file = ttk.Label(self, text="Current File: None", font=("Helvetica", 12, "normal"), justify="center")
        self.current_file.grid(row=8, column=0, columnspan=7, pady=5, padx=10, sticky="nswe")

        self.pack()
        
        # To simplify error handling, I'm gonna use the report_callback_exception method
        tk.Tk.report_callback_exception = self.report_callback_exception
                
        # Start a thread to analyze the drive
        self.analyze_thread = Thread(target=self.start_download).start()
        
    def report_callback_exception(self, *args):
        """
        Method which makes a popup window when an exception occurs
        """
        err = traceback.format_exception(*args)
        # Log the error
        print("".join(err), file=self.log_file)
        # Finally, make a popup window
        messagebox.showerror("Error", "An unknown error occurred while cloning your drive, and DriveClonr cannot continue. Please check the log file for more information.")
        self.log_file.flush()
        exit(1)
        
    
    def start_download(self) -> None:
        """
        Method which traverses the users Google Drive and recursively calls the _download method
        Preconditions: self.service is not None and is a valid Google Drive API service
        """
        print("Starting download", file=self.log_file)
        download_list = []
        if self.config['my_drive']:
            download_list.append("'root' in parents and trashed = false")
            # To get the total files for "my drive" we can make a search query with not 'me' in owners
        if self.config['shared']:
            download_list.append("sharedWithMe and trashed = false")
        if self.config['trashed']:
            download_list.append("trashed = true")

        name_dict = {"'root' in parents and trashed = false": "Your Files", "sharedWithMe and trashed = false": "Shared Files", "trashed = true": "Trashed Files"}
        
        # AT some point I aim to refactor the donwloading code since right now there's a lot of duplicate code
        # But as per usual; i'm too lazy :P
        
        for i in range(len(download_list)):
            query = download_list[i]        
            self.stage['text'] = f"Stage {i + 1} of {len(download_list)}: Cloning {name_dict[download_list[i]]}"
            self.stage.update()
            
            # Make a folder in the destination directory corresponding to name_dict and download all the files in that folder
            if not os.path.exists(f"{self.config['destination']}/{name_dict[download_list[i]]}"):
                print(f"Making directory {self.config['destination']}/{name_dict[download_list[i]]}", file=self.log_file)
                os.mkdir(f"{self.config['destination']}/{name_dict[download_list[i]]}")
            current_dir = f"{self.config['destination']}/{name_dict[download_list[i]]}"
            
            # Get a list of all the root folders
            root_folders = self._make_request(f"mimeType = 'application/vnd.google-apps.folder' and {query}")
            root_files = self._make_request(f"mimeType != 'application/vnd.google-apps.folder' and {query}")
            for folder in root_folders:
                print(f"{time.strftime('%H:%M:%S')} Downloading folder {folder['name']}", file=self.log_file)
                folder_name = self._sanitize_filename(folder['name'])
                self.current_file['text'] = f"Current File: {folder['name']}"
                self.current_file.update()
                if not os.path.exists(f"{current_dir}/{folder_name}"):
                    print(f"Making directory {current_dir}/{folder_name}", file=self.log_file)
                    os.mkdir(f"{current_dir}/{folder_name}")
                folder_id = folder['id']
                self._download(folder_id, f"{current_dir}/{folder_name}")
            for file in root_files:
                print(f"{time.strftime('%H:%M:%S')} Downloading file {file['name']}", file=self.log_file)
                file_name = self._sanitize_filename(file['name'])
                self.current_file['text'] = f"Current File: {file['name']}"
                self.current_file.update()
                extension = self.extensions.get(file['mimeType'], "")
                if not os.path.exists(f"{current_dir}/{file_name}{extension}"):
                    mime_type = self.mime_type_mapping.get(file['mimeType'], None)
                    try:
                        print(f"{time.strftime('%H:%M:%S')} Attempting to download file {file['name']}", file=self.log_file)
                        fileio = self._download_file(file['id'], mime_type)
                        with open(f"{current_dir}/{file_name}{extension}", 'wb') as f:
                            f.write(fileio.getvalue())
                            f.close()
                    except HttpError as e:
                        print(f"{time.strftime('%H:%M:%S')} Error downloading file {file['name']}. Trying to recover...", file=self.log_file)
                        if e.reason == "This file is too large to be exported.":
                            print(f"{time.strftime('%H:%M:%S')} Downloading file {file['name']} using export links", file=self.log_file)
                            self._download_using_export_links(file, current_dir, file_name, extension)
                        else:
                            print(f"{time.strftime('%H:%M:%S')} Unknown error occured downloading file {file['name']}: {e}", file=self.log_file)
                            self.failed_files.append((file['name'], file['id'], e.reason))

        # If we're here, cloning is complete. Show the new screen
        with open(f"{self.config['destination']}/failedfiles.txt", 'w') as f:
            for file in self.failed_files:
                f.write(f"{file[0]} ({file[1]}): {file[2]}\n")
            f.close()
        self.log_file.flush()
        self.pb.stop()
        self.pb.destroy()
        self.current_file.destroy()
        self.header_text['text'] = "Cloning Complete!"  
        # Set self.stage to apply word wrap
        self.stage['wraplength'] = 500
        self.stage['text'] = "Your Google Drive has been cloned to your computer. You can view failed files in failedfiles.txt, found in the same directory as your cloned files."
        self.directory_button = tk.Label(self, text="Open Cloned Directory", fg="blue", cursor="hand2")
        self.directory_button.bind("<Button-1>", lambda e: self._open_directory())
        self.directory_button.grid(row=3, column=15, pady=10)
        
    def _download(self, folder_id: str, current_dir: str) -> None:
        """
        Helper method for start_download which downloads all the files in a given folder
        """
    
        # Get a list of all folders in the folder_id given
        root_folders = self._make_request(f"mimeType = 'application/vnd.google-apps.folder' and '{folder_id}' in parents")
        root_files = self._make_request(f"mimeType != 'application/vnd.google-apps.folder' and '{folder_id}' in parents")
        for folder in root_folders:
            print(f"{time.strftime('%H:%M:%S')} Downloading folder {folder['name']}", file=self.log_file)
            folder_name = self._sanitize_filename(folder['name'])
            folder_id = folder['id']
            self.current_file['text'] = f"Current File: {folder['name']}"
            self.current_file.update()
            if not os.path.exists(f"{current_dir}/{folder_name}"):
                print(f"Making directory {current_dir}/{folder_name}", file=self.log_file)
                os.mkdir(f"{current_dir}/{folder_name}")
            self._download(folder_id, f"{current_dir}/{folder_name}")
        for file in root_files:
            print(f"{time.strftime('%H:%M:%S')} Downloading file {file['name']}", file=self.log_file)
            file_name = self._sanitize_filename(file['name'])
            self.current_file['text'] = f"Current File: {file['name']}"
            self.current_file.update()            
            extension = self.extensions.get(file['mimeType'], "")
            if not os.path.exists(f"{current_dir}/{file_name}{extension}"):
                mime_type = self.mime_type_mapping.get(file['mimeType'], None)
                try:
                    print(f"{time.strftime('%H:%M:%S')} Attempting to download file {file['name']}", file=self.log_file)
                    fileio = self._download_file(file['id'], mime_type)
                    with open(f"{current_dir}/{file_name}{extension}", 'wb') as f:
                        f.write(fileio.getvalue())
                        f.close()
                except HttpError as e:
                    print(f"{time.strftime('%H:%M:%S')} Error downloading file {file['name']}. Trying to recover...", file=self.log_file)
                    if e.reason == "This file is too large to be exported.":
                        print(f"{time.strftime('%H:%M:%S')} Downloading file {file['name']} using export links", file=self.log_file)
                        self._download_using_export_links(file, current_dir, file_name, extension)
                    else:
                        print(f"{time.strftime('%H:%M:%S')} Unknown error occured downloading file {file['name']}: {e}", file=self.log_file)
                        self.failed_files.append((file['name'], file['id'], e.reason))

    def _open_directory(self) -> None:
        """
        Opens the cloned directory in the file explorer
        Precondition: The cloned directory exists
        """
        os.startfile(self.config['destination'])

    def _download_using_export_links(self, file, current_dir: str, file_name: str, extension: str) -> None:
        """
        Method used to work around the Google Drive API export size limitation
        Precondition: The file is too large to be exported, and the file is a Google Workspace Document
        """
        print(f"{time.strftime('%H:%M:%S')} Starting download of {file['name']} using export links", file=self.log_file)
        print(f"{time.strftime('%H:%M:%S')} Creating temporary permission for file {file['name']}", file=self.log_file)
        id = self.service.permissions().create(fileId=file['id'], body={"role": "reader", "type": "anyone", "allowFileDiscovery": False}).execute()                 
        links = file['exportLinks']
        link = links[self.mime_type_mapping[file['mimeType']]]

        # Now simply making a request to the link is insufficient because we need to add the authorization header
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",                        
        }                                 
        print(f"{time.strftime('%H:%M:%S')} Making request to {link}", file=self.log_file)
        # Now we have a direct link to the file. We can download it using requests
        r = requests.get(link, headers=headers)
        with open(f"{current_dir}/{file_name}{extension}", 'wb') as f:
            print(f"{time.strftime('%H:%M:%S')} Writing file {file['name']} to disk", file=self.log_file)
            f.write(r.content)
            f.close()
        # Now we need to revert the permissions back to what they were before   
        print(f"{time.strftime('%H:%M:%S')} Removing temporary permission for file {file['name']}", file=self.log_file)
        self.service.permissions().delete(fileId=file['id'], permissionId=id['id']).execute()

    def _make_request(self, request: str) -> list[dict]:
        """
        Method to simplify making requests to the Google Drive API
        Preconditions: request is a valid query string
        """
        # We're going to add a list of extras to the query to simplify the code
        # We're going to remove forms, sites, colab, and shortcuts
        response = self.service.files().list(fields="nextPageToken, files(id, name, mimeType, exportLinks)", q=f"{request} and mimeType != 'application/vnd.google-apps.form' and mimeType != 'application/vnd.google-apps.site' and mimeType != 'application/vnd.google-apps.shortcut' and mimeType != 'application/vnd.google-apps.map' and mimeType != 'application/vnd.google-apps.script' and mimeType != 'application/vnd.google-apps.drive-sdk'").execute()
        folders = response.get('files', [])
        nextPageToken = response.get('nextPageToken')
        while nextPageToken:
            response = self.service.files().list(q=f"{request}", pageToken=nextPageToken).execute()
            folders.extend(response.get('files', []))
            nextPageToken = response.get('nextPageToken')
        return folders

    def _sanitize_filename(self, filename: str) -> str:
        """
        Method used to remove invalid characters from a filename
        """
        # Define the pattern to match characters not allowed in a filename
        invalid_chars_pattern = r'[<>:"/\\|?*\x00-\x1F\x7F]+'
        # Define the pattern to match emojis
        emoji_pattern = re.compile("["
                                u"\U0001F600-\U0001F64F"  # Emoticons
                                u"\U0001F300-\U0001F5FF"  # Symbols & Pictographs
                                u"\U0001F680-\U0001F6FF"  # Transport & Map Symbols
                                u"\U0001F1E0-\U0001F1FF"  # Flags (iOS)
                                u"\U00002702-\U000027B0"  # Dingbats
                                u"\U000024C2-\U0001F251" 
                                "]+", flags=re.UNICODE)
        
        # Remove the matched characters from the filename
        sanitized_filename = re.sub(invalid_chars_pattern, '', filename)

        # Remove emojis from the filename
        sanitized_filename = emoji_pattern.sub('', sanitized_filename)

        # Check for reserved folder names in Windows - because Microsoft doesn't wanna let go of DOS
        reserved_names = ['con', 'aux', 'nul', 'prn', 'com1', 'lpt1', 'com2', 'lpt2',
                        'com3', 'lpt3', 'com4', 'lpt4', 'com5', 'lpt5', 'com6',
                        'lpt6', 'com7', 'lpt7', 'com8', 'lpt8', 'com9', 'lpt9']

        sanitized_filename = sanitized_filename.strip()
        if sanitized_filename.lower() in reserved_names:
            sanitized_filename += '_'

        return sanitized_filename.strip()
    
    def _download_file(self, file_ID, mime_type = None) -> io.BytesIO:
        """
        Method to download a file with the specified MIME type
        Precondition:
        if mime_type is None:
            file_ID is a valid file ID, and is not a Google Workspace Document
        if mime_type is not None:
            file_ID is a valid file ID, and is a Google Workspace Document
            mime_type is a valid MIME type, and is a valid export option for the file
        """
        if mime_type is None:
            request = self.service.files().get_media(fileId=file_ID, supportsAllDrives=True, supportsTeamDrives=True)
        else:
            request = self.service.files().export_media(fileId=file_ID, mimeType=mime_type)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        return fh

if __name__ == "__main__":
    # If this file is run directly, run in debug mode
    root = tk.Tk()
    root.title("DriveClonr")
    root.geometry("300x300")
    DriveDownloadr(root, None, None).pack()
    root.mainloop()
    
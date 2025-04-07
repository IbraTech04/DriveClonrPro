import shutil
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import os
from typing import TextIO 
from ReadyToStart import ReadyToStart
import winreg
import psutil
GOOGLE_WORKSPACE_MIMETYPES = {"Docs": "application/vnd.google-apps.document", "Sheets": "application/vnd.google-apps.spreadsheet", "Slides": "application/vnd.google-apps.presentation", "Drawings": "application/vnd.google-apps.drawing"}

MIMETYPES = {"Word": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "Excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "PowerPoint": "application/vnd.openxmlformats-officedocument.presentationml.presentation", "PDF": "application/pdf", "JPEG": "image/jpeg", "PNG": "image/png", "SVG": "image/svg+xml", "HTML": "text/html", "Plain Text": "text/plain", "OpenOffice Writer": "application/vnd.oasis.opendocument.text", "OpenOffice Calc": "application/vnd.oasis.opendocument.spreadsheet", "OpenOffice Impress": "application/vnd.oasis.opendocument.presentation"}

class ConfigWindow(tk.Frame):
    """
    Configuration information for the Clone of the drive
    """
    def __init__(self, parent: tk.Tk, service, log_file: TextIO):
        super().__init__(parent)
        self.parent = parent
        self.service = service
        self.log_file = log_file
        print("Entered ConfigWindow", file=self.log_file)
        
        # HEADER AND SUBHEADING        
        self.header = ttk.Label(self.parent, text="Configure your Clonr", font=("Helvetica", 16, "bold"))
        self.header.pack(pady=10)
        self.subheading = ttk.Label(self.parent, text="Select what you want to clone", font=("Helvetica", 12, "normal"))
        self.subheading.pack(pady=5)
        
        self.info_frame = ttk.LabelFrame(self.parent, text="Source Data")

        # Shared with Me and My Drive checkboxes
        self.shared_var = tk.BooleanVar()
        self.shared_checkbox = ttk.Checkbutton(self.info_frame, text="Shared with Me", variable=self.shared_var)

        self.my_drive_var = tk.BooleanVar()
        self.my_drive_checkbox = ttk.Checkbutton(self.info_frame, text="My Drive", variable=self.my_drive_var)
        self.my_drive_checkbox.pack()
        
        self.trashed = tk.BooleanVar()
        self.trashed_checkbox = ttk.Checkbutton(self.info_frame, text="Trashed files", variable=self.trashed)
        self.trashed_checkbox.pack()
        
        self.shared_checkbox.pack()
        
        # Create a greyed out box for Google Photos - This is a feature coming soon
        self.google_photos_var = tk.BooleanVar()
        self.google_photos_checkbox = ttk.Checkbutton(self.info_frame, text="Google Photos", variable=self.google_photos_var)
        self.google_photos_checkbox.pack()
        
        
        self.info_frame.pack(pady=10)
        
        # Chart with Google Workspace document types and export options
        self.doc_frame = ttk.LabelFrame(self.parent, text="Export Options")
        self.doc_frame.pack(pady=10)

        # Document type labels and export options
        self.doc_labels = ["Docs", "Slides", "Sheets", "Drawings"]
        self.doc_export_options = {
            "Docs": ["PDF", "Word", "OpenOffice Writer"],
            "Slides": ["PDF", "PowerPoint", "OpenOffice Impress"],
            "Sheets": ["PDF", "Excel", "OpenOffice Calc"],
            "Drawings": ["PNG", "PDF", "JPEG", "SVG"]
        }

        self.doc_vars = []
        self.doc_dropdowns = []

        for doc_label in self.doc_labels:
            var = tk.StringVar()

            if doc_label == "Drawings":
                var.set("PNG")  # Default export option for Drawings
            else:
                var.set(self.doc_export_options[doc_label][1])  # Default Office equivalent

            label = ttk.Label(self.doc_frame, text=doc_label)
            label.pack(side=tk.LEFT, padx=10)

            dropdown = ttk.OptionMenu(self.doc_frame, var, var.get(), *self.doc_export_options[doc_label])
            dropdown.pack(side=tk.LEFT)

            self.doc_vars.append(var)
            self.doc_dropdowns.append(dropdown)


        # Destination directory selection
        self.destination_frame = ttk.Frame(self.parent)
        self.destination_frame.pack(pady=10)

        self.destination_label = ttk.Label(self.destination_frame, text="Destination Directory:")
        self.destination_label.pack(side=tk.LEFT)

        self.destination_entry = ttk.Entry(self.destination_frame, width=40)
        self.destination_entry.pack(side=tk.LEFT, padx=10)

        self.browse_button = ttk.Button(self.destination_frame, text="Browse", command=self.browse_destination)
        self.browse_button.pack(side=tk.LEFT)

        self.save_button = ttk.Button(self.parent, text="Save Configuration", command=self.save_configuration)
        self.save_button.pack(pady=20)
        
        # Learn what we can and can't clone:
        self.learn_more = ttk.Button(self.parent, text="Learn what DriveClonrPro can and cannot clone", command=self.learn_more)
        self.learn_more.pack(pady=20)
    
    def learn_more(self):
        # Open a popup window explaining what we can and can't clone
        self.learn_more_window = tk.Toplevel(self.parent)
        self.learn_more_window.title("What can and can't be cloned?")
        self.learn_more_window.geometry("500x500")
        self.learn_more_window.resizable(False, False)

        # Create a frame for better organization of content
        frame = ttk.Frame(self.learn_more_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Add a title label
        title_label = ttk.Label(frame, text="What can and can't be cloned?", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # Add content labels with improved formatting
        content_labels = [
            "DriveClonrPro can clone:",
            "• Files and folders in My Drive",
            "• Google Workspace documents in My Drive (exported to your chosen format)",
            "• Most files and folders shared with you*",
            "  * Some files shared with you have download and export restrictions,",
            "    which DriveClonrPro cannot bypass",
            "  * Some files are inaccessible through DriveClonr due to limitations",
            "    in the Google Drive API",
            "• Files and folders in your Trash"
        ]

        for label_text in content_labels:
            label = ttk.Label(frame, text=label_text, wraplength=450, justify=tk.LEFT)
            label.pack(anchor=tk.W, pady=5)

        # Add a note label
        note_label = ttk.Label(frame, text="Note: DriveClonrPro cannot bypass certain restrictions imposed by "
                                            "Google Drive or Google Workspace.", font=("Arial", 10), foreground="gray")
        note_label.pack(pady=10)

        # DriveClonrPro can clone: 
        # - Files and folders in My Drive
        # - Google Workspace documents in My Drive (Exported to your chosen format) despite their size
        # - Most files and folders shared with you*
            # * Some files shared with you have download and export restrictions, which DriveClonrPro cannot bypass
            # * Some files are inaccessible through DriveClonr due to limitations in the Google Drive API
        # - Files and folders in your Trash

    def browse_destination(self):
        """
        Opens a file dialog to select the destination directory
        """
        destination_path = filedialog.askdirectory()
        self.destination_entry.delete(0, tk.END)
        self.destination_entry.insert(tk.END, destination_path)

    def save_configuration(self):
        """
        Saves the configuration to a dictionary and passes it to the CloneWindow
        Kills the ConfigWindow
        """
        # Step One: Make sure the user has entered a valid destination  
        destination = self.destination_entry.get()
        if not destination or not os.path.isdir(destination):
            print(f"Invalid destination directory. Entered: {destination}", file=self.log_file)
            tk.messagebox.showerror("Error", "Please enter a valid destination directory.")
            return

        # Step one and a half: Make sure the user has selected at least one of Shared with Me or My Drive
        if not self.shared_var.get() and not self.my_drive_var.get() and not self.trashed.get():
            print("No source(s) selected", file=self.log_file)
            tk.messagebox.showerror("Error", "Please select at least one of Shared with Me or My Drive.")
            return

        # Get the total size of the Google Drive, along with the total free space on the host drive
        drive_size = self.service.about().get(fields="storageQuota").execute()["storageQuota"]["usage"]
        drive_size = int(drive_size) / (1024 ** 3)
        print(f"Drive size: {drive_size} GB", file=self.log_file)
        
        clone_directory = self.destination_entry.get()
        free = shutil.disk_usage(clone_directory)[2]
        free = free / (1024 ** 3)
        print(f"Free space: {free} GB", file=self.log_file)

        # If the drive is larger than the free space, then the program will not run
        if drive_size > free:
            print("Not enough space", file=self.log_file)
            # Make a popup warning the user that there is not enough space
            tk.showwarning("Not Enough Space!", "There is not enough space on the drive you selected to clone your Google Drive. Please select a different drive.")
            return            

        # Step Two: Create a dict with the configuration information relative to mime types
        config = {}
        config["destination"] = destination
        config["mime_types"] = {}
        
        # Step Three: Add the mime types and export options for Google Workspace documents
        for i, doc_label in enumerate(self.doc_labels):
            config["mime_types"][GOOGLE_WORKSPACE_MIMETYPES[doc_label]] = MIMETYPES[self.doc_vars[i].get()]
        
        # Finally, add the check status for Shared with Me and My Drive
        config["shared"] = self.shared_var.get()
        config["my_drive"] = self.my_drive_var.get()
        config["trashed"] = self.trashed.get()
        config["photos"] = self.google_photos_var.get()
        
        # Finally, check the registry for LongFilePathEnabled and set it to 1 if it's not already set
        # This is required for Windows to be able to create files with paths longer than 260 characters
        print(f"Current Config: {config}", file=self.log_file)
        if os.name == "nt":
            print("Checking registry for LongPathsEnabled", file=self.log_file)
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Control\\FileSystem", 0, winreg.KEY_READ)
                value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
                if value != 1:
                    print("LongPathsEnabled not set to 1", file=self.log_file)
                    print("Attempting to change LongPathsEnabled to 1", file=self.log_file)
                    # Make a warning saying "we need to change this"
                    tk.messagebox.showwarning("Warning", "Clonr needs to change a registry setting to work properly. (LongPathsEnabled) This requires UAC elevation. Please click OK to continue.")
                    # Run the file called disable-file-limit.reg
                    os.system("disable-file-limit.reg")
                    tk.messagebox.showinfo("Success", "The registry setting has been changed successfully! DriveClonr can continue.")     
                    print("LongPathsEnabled set to 1", file=self.log_file)         
            except Exception as e:
                print("Error: ", e, file=self.log_file)
                tk.messagebox.showerror("Error", "An unknown error occurred while trying to change the registry setting. DriveClonr cannot continue. Please check the logfile for more information. If you open an issue on GitHub, please include the logfile.")
                exit(1)

        #Destroy all the widgets in the window
        widgets = self.parent.winfo_children()
        for widget in widgets:
            widget.destroy()
        super().pack_forget()
        super().destroy()
        ReadyToStart(self.parent, self.service, self.log_file, config).pack()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("ClonrDebug")
    ConfigWindow(root, None).pack()
    root.mainloop()
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import os 
from ReadyToStart import ReadyToStart
import winreg

GOOGLE_WORKSPACE_MIMETYPES = {"Docs": "application/vnd.google-apps.document", "Sheets": "application/vnd.google-apps.spreadsheet", "Slides": "application/vnd.google-apps.presentation"}

class ConfigWindow(tk.Frame):
    """
    Configuration information for the Clone of the drive
    """
    def __init__(self, parent: tk.Tk, service):
        super().__init__(parent)
        self.parent = parent
        self.service = service

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
        self.google_photos_checkbox = ttk.Checkbutton(self.info_frame, text="Google Photos", variable=self.google_photos_var, state=tk.DISABLED)
        self.google_photos_checkbox.pack()
        
        
        self.info_frame.pack(pady=10)
        
        # Chart with Google Workspace document types and export options
        self.doc_frame = ttk.LabelFrame(self.parent, text="Export Options")
        self.doc_frame.pack(pady=10)

        # Document type labels and export options
        self.doc_labels = ["Sheets", "Docs", "Slides"]
        self.doc_export_options = {
            "Sheets": "Excel",
            "Docs": "Word",
            "Slides": "PowerPoint"
        }

        self.doc_vars = []
        self.doc_dropdowns = []

        for doc_label in self.doc_labels:
            var = tk.StringVar()
            var.set("PDF")  # Default export option

            label = ttk.Label(self.doc_frame, text=doc_label)
            label.pack(side=tk.LEFT, padx=10)

            dropdown = ttk.OptionMenu(self.doc_frame, var, "PDF", "PDF", self.doc_export_options[doc_label])
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

    def browse_destination(self):
        destination_path = filedialog.askdirectory()
        self.destination_entry.delete(0, tk.END)
        self.destination_entry.insert(tk.END, destination_path)

    def save_configuration(self):
        # Step One: Make sure the user has entered a valid destination  
        destination = self.destination_entry.get()
        if not destination or not os.path.isdir(destination):
            tk.messagebox.showerror("Error", "Please enter a valid destination directory.")
            return

        # Step one and a half: Make sure the user has selected at least one of Shared with Me or My Drive
        if not self.shared_var.get() and not self.my_drive_var.get() and not self.trashed.get():
            tk.messagebox.showerror("Error", "Please select at least one of Shared with Me or My Drive.")
            return

        # Step Two: Create a dict with the configuration information relative to mime types
        config = {}
        config["destination"] = destination
        config["mime_types"] = {}
        
        # Step Three: Add the mime types and export options for Google Workspace documents
        for i, doc_label in enumerate(self.doc_labels):
            config["mime_types"][GOOGLE_WORKSPACE_MIMETYPES[doc_label]] = self.doc_vars[i].get()
        
        # Finally, add the check status for Shared with Me and My Drive
        config["shared"] = self.shared_var.get()
        config["my_drive"] = self.my_drive_var.get()
        config["trashed"] = self.trashed.get()
        
        # Finally, check the registry for LongFilePathEnabled and set it to 1 if it's not already set
        # This is required for Windows to be able to create files with paths longer than 260 characters
        
        if os.name == "nt":
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Control\\FileSystem", 0, winreg.KEY_READ)
                value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
                if value != 1:
                    # Make a warning saying "we need to change this"
                    tk.messagebox.showwarning("Warning", "Clonr needs to change a registry setting to work properly. (LongPathsEnabled) This requires UAC elevation. Please click OK to continue.")
                    # Run the file called disable-file-limit.reg
                    os.system("disable-file-limit.reg")
                    tk.messagebox.showinfo("Success", "The registry setting has been changed successfully! DriveClonr can continue.")              
            except FileNotFoundError:
                pass

        #Destroy all the widgets in the window
        widgets = self.parent.winfo_children()
        for widget in widgets:
            widget.destroy()

        
        super().pack_forget()
        super().destroy()
        ReadyToStart(self.parent, self.service, config).pack()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("ClonrDebug")
    ConfigWindow(root, None).pack()
    root.mainloop()
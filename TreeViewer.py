import tkinter as tk
from tkinter import ttk
import tkinter.ttk as ttk
from typing import Any
from typing_extensions import Literal
from ttkwidgets import CheckboxTreeview
from TreeNode import TreeNode
from threading import Thread

# DEPRECIATED CLASS - Ultimately here only for archival. The Checkboxtreeviewer was a pain in the ass and honestly didn't work too well

class TreeViewer(tk.Frame):
    def __init__(self, parent: tk.Tk, service):
        super().__init__(parent)
        self.service = service
        self.parent = parent
        
        # Add text saying "loading your drive" or something
        self.loading_text = ttk.Label(self, text="Loading your drive... Please Wait", font=("Helvetica", 16, "bold"))
        self.loading_text.grid(row=0, column=0, pady=10)

        self.subtext = ttk.Label(self, text="This may take a while depending on the size of your drive.\nDriveClonr may hang during this process", font=("Helvetica", 12, "italic"))
        self.subtext.grid(row=1, column=0, pady=5)
                
        self.pb = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='indeterminate',
            length=280
        )
        self.pb.start(10)
        self.pb.grid(row=2, column=0, pady=10)
    
        self.pack()
        Thread(target=self.init_drive_selection).start()

    def init_drive_selection(self):                
        self.treeview = CheckboxTreeview(self, show="tree", selectmode="browse")    
        self.treeview.configure(columns=("size", "modified"))            
        self.populate_treeview()
        self.loading_text.destroy()
        self.subtext.destroy()
        self.pb.destroy()
        self.header = ttk.Label(self, text="Select the folders you want to clone", font=("Helvetica", 16, "bold"))
        self.header.grid(row=0, column=0, pady=10)
        self.subheader = ttk.Label(self, text="You can select individual files by clicking on them", font=("Helvetica", 12, "italic"))       
        self.treeview.grid(row=1, column=0, pady=10)
        # make a select all and deselect all button
        # make sure they are on the same line
        self.select_all_button = ttk.Button(self, text="Select All", command=self.select_all)
        self.select_all_button.grid(row=2, column=0, pady=10)
        self.deselect_all_button = ttk.Button(self, text="Deselect All", command=self.deselect_all)
        self.deselect_all_button.grid(row=2, column=1, pady=10)
        self.next_button = ttk.Button(self, text="Next", command=self.next)
        self.next_button.grid(row=3, column=0, pady=10)
        self.pack()

    def select_all(self):
        for item in self.treeview.get_children():
            self.treeview.change_state(item, "checked")
            self._change_state_recursive(item, "checked")
            
    def _change_state_recursive(self, item, state):
        # This method will recursively select all children of a given item
        # First, select the item
        self.treeview.change_state(item, state)
        # Then, recurse over all children
        for child in self.treeview.get_children(item):
            self._change_state_recursive(child, state)
        
    def deselect_all(self):
        for item in self.treeview.get_children():
            self.treeview.change_state(item, "unchecked")
            self._change_state_recursive(item, "unchecked")
    
    def populate_treeview(self):
        """
        Method which traverses a users Google Drive and populates the treeview with the files and folders
        """
        self.treeview.insert("", "end", "root", text="My Drive")
        self._populate("root")

        # Now we do the same thing for shared with me
        # However we need to treat shared with me differently
        # we need to do all the folders first, then all the files
        # This is because Google Drive is stupid and allows shared files to be out of their folders, but also have the actual shared folder iwth that same file in it
        self.treeview.insert("", "end", "sharedWithMe", text="Shared with me")
        self._populate_shared("sharedWithMe", True)

    def _populate_shared(self, parent_id: str, start = False):
        if start:
            shared_folders = self._make_request("sharedWithMe and mimeType = 'application/vnd.google-apps.folder' and trashed = false and mimeType != 'application/vnd.google-apps.shortcut'")
        else:
            shared_folders = self._make_request(f"'{parent_id}' in parents and trashed = false and mimeType = 'application/vnd.google-apps.folder' and mimeType != 'application/vnd.google-apps.shortcut'")
        
        for i, folder in enumerate(shared_folders):
            folder_id = folder['id']
            folder_name = folder['name']
            try:
                self.treeview.insert(parent_id, "end", folder_id, text=folder_name)
            except:
                pass
            self._populate_shared(folder_id)
        
        # Now we do the same thing for files
        if start:
            files = self._make_request("sharedWithMe and mimeType != 'application/vnd.google-apps.folder' and trashed = false and mimeType != 'application/vnd.google-apps.shortcut'")
        else:
            files = self._make_request(f"'{parent_id}' in parents and trashed = false and mimeType != 'application/vnd.google-apps.folder' and mimeType != 'application/vnd.google-apps.shortcut'")
        
        for i, file in enumerate(files):
            file_id = file['id']
            file_name = file['name']
            try:
                self.treeview.insert(parent_id, "end", file_id, text=file_name)
            except:
                pass
        
                
    def _populate(self, parent_id: str):
        files_and_folders = self._make_request(f"'{parent_id}' in parents and trashed = false and mimeType != 'application/vnd.google-apps.shortcut' and mimeType != 'application/vnd.google-apps.form'")
        for item in files_and_folders:
            item_id = item['id']
            item_name = item['name']
            item_mimeType = item['mimeType']
            
            if item_id == "1aD2aFjODO5PEyhYj00jvpr0UDpVxaDbp_cLZGK_Eh7E ":
                x=1
            
            if item_mimeType == 'application/vnd.google-apps.folder':
                # Add the folder to the treeview
                self.treeview.insert(parent_id, "end", item_id, text=item_name)
                self._populate(item_id)  # Recursively populate the subfolder
    
            else:
                self.treeview.insert(parent_id, "end", item_id, text=item_name)


    def find_item_path(self, treeview, item_id):
        """
        Find the path to locate the item with the given ID in the CheckboxTreeview.
        Returns a list representing the path of item IDs from root to the target item.
        """
        path = []
        self._traverse_treeview(treeview, "", item_id, path)
        return path

    def _traverse_treeview(self, treeview, parent_id, target_id, path):
        """
        Helper function to traverse the CheckboxTreeview and find the path to the target ID.
        """
        children = treeview.get_children(parent_id)

        for item_id in children:
            if item_id == target_id:
                path.append(item_id)
                return True

            if self._traverse_treeview(treeview, item_id, target_id, path):
                path.append(item_id)
                return True

        return False
            
    def _make_request(self, request: str) -> list:
        response = self.service.files().list(fields="nextPageToken, files(id, name, mimeType)", q=f"{request}").execute()
        folders = response.get('files', [])
        nextPageToken = response.get('nextPageToken')
        while nextPageToken:
            response = self.service.files().list(q=f"{request}", pageToken=nextPageToken).execute()
            folders.extend(response.get('files', []))
            nextPageToken = response.get('nextPageToken')
        
        # We need to check for and remove duplicate ids in the request 
        ids = set()
        to_return = []
        for i, j in enumerate(folders):
            if j['id'] not in ids:
                to_return.append(j)
                ids.add(j['id'])
        
        return to_return

    def next(self):
        root = TreeNode(None, [])
        items = self.treeview.get_checked()
        for item in items:
            # Check if the item is checked
            folder_ref = self.treeview.item(item)
            if "checked" in folder_ref['tags'] or "tristate" in folder_ref["tags"]:
                root.add_child(TreeNode(item))
                self._next_helper(item, root.children[-1])
        print("Done - We're not stuck in infinite recursion, but we also don't know if the tree was built properly")
            
    def _next_helper(self, curr_id: str, curr_node: TreeNode):
        # Step 1: get all children of curr_id
        children = self.treeview.get_children(curr_id)
        for child in children:
            folder_ref = self.treeview.item(child)
            if "checked" in folder_ref['tags'] or "tristate" in folder_ref["tags"]:     
                curr_node.add_child(TreeNode(child))
                self._next_helper(child, curr_node.children[-1])
            
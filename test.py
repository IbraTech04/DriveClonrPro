import tkinter as tk
import tkinter.ttk as ttk
from ttkwidgets import CheckboxTreeview


def export_checked_items():
    checked_items = []
    for folder in treeview.get_children():
        folder_ref = treeview.item(folder)
        if "checked" in folder_ref['tags'] or "tristate" in folder_ref["tags"]:
            print(folder)
        


root = tk.Tk()

treeview = CheckboxTreeview(root)
treeview.pack()

treeview.insert("", "end", "1", text="1")
treeview.insert("1", "end", "11", text="11")
treeview.insert("1", "end", "12",  text="12")
treeview.insert("11", "end", "111", text="111")
treeview.insert("", "end", "2", text="2")

# Export button
export_button = ttk.Button(root, text="Export Checked Items", command=export_checked_items)
export_button.pack()

root.mainloop()

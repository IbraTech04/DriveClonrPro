import os
import platform
import re
import winreg
import requests

from typing import Optional, Union
from .model.tree_node import DownloadableNode, DriveNode

from core.constants import MIMETYPE_EXTENSIONS


def check_windows_registry_longpath():
    if platform.system() != "Windows":
        return True
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\FileSystem",
            0,
            winreg.KEY_READ
        )
        value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
        return value == 1
    except Exception:
        return False


def prune_checked_nodes(node: DownloadableNode) -> bool:
    """
    Mutates the given DriveNode tree in place by pruning unchecked nodes 
    that do not have any checked descendants.

    Returns:
      True if this node should be kept (i.e. it is checked or it has any remaining children),
      and False if it should be pruned.
    """
    if not node:
        return False
    # Process children recursively and filter out those that should be pruned.
    new_children = []
    for child in node.children:
        if prune_checked_nodes(child):
            new_children.append(child)
    node.children = new_children  # Update the children in place.
    
    # Keep this node if it is checked or if it has any children after pruning.
    return node.is_checked or bool(node.children)



def sanitize_filename(filename: str) -> str:
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


def get_extension(mime_type: str) -> str:
    """
    Returns the file extension for a given MIME type.
    """
    if mime_type in MIMETYPE_EXTENSIONS:
        return MIMETYPE_EXTENSIONS[mime_type]
    return ""


def download_from_export_link(token: str, link: str):
    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = requests.get(link, headers=headers, stream=True)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to download file: {response.status_code}")

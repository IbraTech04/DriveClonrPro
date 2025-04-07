import os
import platform
import winreg

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

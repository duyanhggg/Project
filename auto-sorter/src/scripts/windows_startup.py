import os
import winshell
from win32com.client import Dispatch

def add_to_startup():
    try:
        startup = winshell.startup()
        script_path = os.path.abspath(__file__)
        shortcut_path = os.path.join(startup, "AutoSorter.lnk")

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = script_path
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.IconLocation = script_path
        shortcut.save()
    except Exception as e:
        print(f"Cannot add to startup: {e}")

if __name__ == "__main__":
    add_to_startup()
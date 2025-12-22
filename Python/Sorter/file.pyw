import os
import shutil
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from plyer import notification
import string
from infi.systray import SysTrayIcon
import sys

# Global variables
is_enabled = True
current_drive = "D:\\"
observer = None
systray = None

# File extension -> folder mapping
ext_to_type = {
    "png": "Images",
    "jpg": "Images",
    "jpeg": "Images",
    "gif": "Images",
    "pdf": "Docs",
    "docx": "Docs",
    "txt": "Docs",
    "xlsx": "Docs",
    "mp3": "Music",
    "wav": "Music",
    "mp4": "Videos",
    "mkv": "Videos",
    "avi": "Videos",
    "mov": "Videos",
    "7z": "Others",
    "gz": "Others",
    "rar": "Others",
    "zip": "Others",
    "exe": "Programs",
    "msi": "Programs",
    "iso": "DiskImages",
    "img": "DiskImages",
}

# Setup logging
def setup_logging(drive):
    log_dir = os.path.join(drive, "Logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "auto_sorter.log")
    
    # Remove old handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
        force=True
    )

def get_available_drives():
    """Get a list of available drives on the system"""
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives

def move_file(file_path, source):
    """Move the file to the appropriate folder"""
    if os.path.isfile(file_path):
        ext = os.path.splitext(file_path)[1].lower().lstrip(".")
        folder = ext_to_type.get(ext, "Misc")
        dest_path = os.path.join(source, folder)
        os.makedirs(dest_path, exist_ok=True)
        try:
            shutil.move(file_path, os.path.join(dest_path, os.path.basename(file_path)))
            msg = f"Moved '{os.path.basename(file_path)}' to '{folder}'"
            logging.info(msg)
            notification.notify(
                title="AutoSorter",
                message=msg,
                app_name="AutoSorter",
                timeout=3
            )
        except Exception as e:
            logging.error(f"Error when moving file '{file_path}': {e}")

class Handler(FileSystemEventHandler):
    """Handle events when new files are created"""
    def __init__(self, source):
        self.source = source
    
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(10)
            msg = f"New file detected: {os.path.basename(event.src_path)}"
            logging.info(msg)
            notification.notify(
                title="AutoSorter",
                message=msg,
                app_name="AutoSorter",
                timeout=3
            )
            move_file(event.src_path, self.source)

def start_observer(drive):
    """Start the observer for the selected drive"""
    global observer, current_drive
    
    # Stop any previous observer if running
    if observer and observer.is_alive():
        observer.stop()
        observer.join()
    
    current_drive = drive
    setup_logging(drive)
    
    # Sort existing files on the drive
    for file in os.listdir(drive):
        file_path = os.path.join(drive, file)
        if os.path.isfile(file_path):
            move_file(file_path, drive)
    
    # Start a new observer for the drive
    event_handler = Handler(drive)
    observer = Observer()
    observer.schedule(event_handler, drive, recursive=False)
    observer.start()
    
    msg = f"Monitoring: {drive}"
    logging.info(msg)
    notification.notify(
        title="AutoSorter",
        message=msg,
        app_name="AutoSorter",
        timeout=3
    )
    
    # Update systray menu
    update_systray()

def on_quit(systray):
    """Exit the program"""
    if observer:
        observer.stop()
    logging.info("Exiting the program.")
    os._exit(0)

def on_toggle(systray):
    """Enable/disable automatic sorting"""
    global is_enabled
    is_enabled = not is_enabled
    
    if is_enabled:
        start_observer(current_drive)
        msg = "Automatic sorting enabled"
        notification.notify(
            title="AutoSorter",
            message=msg,
            app_name="AutoSorter",
            timeout=3
        )
    else:
        if observer:
            observer.stop()
        msg = "Automatic sorting disabled"
        notification.notify(
            title="AutoSorter",
            message=msg,
            app_name="AutoSorter",
            timeout=3
        )
    
    update_systray()

def on_select_drive(systray, drive):
    """Select a new drive"""
    if is_enabled:
        start_observer(drive)

def create_menu():
    """Create dynamic menu"""
    drives = get_available_drives()
    
    # Menu ổ đĩa
    drive_menu = []
    for drive in drives:
        mark = "✓ " if drive == current_drive else "   "
        drive_menu.append((f"{mark}{drive}", None, lambda s, d=drive: on_select_drive(s, d)))

    toggle_text = "Disable automatic sorting" if is_enabled else "Enable automatic sorting"

    menu = (
        (toggle_text, None, on_toggle),
        ("Select drive", None, tuple(drive_menu)),
    )
    
    return menu

def update_systray():
    """Update the systray menu"""
    global systray
    if systray:
        systray.update(menu_options=create_menu())

def add_to_startup():
    """Add to startup"""
    try:
        import winshell
        from win32com.client import Dispatch

        startup = winshell.startup()
        script_path = os.path.abspath(sys.argv[0])
        shortcut_path = os.path.join(startup, "AutoSorter.lnk")

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = script_path
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.IconLocation = script_path
        shortcut.save()
    except Exception as e:
        logging.error(f"Cannot add to startup: {e}")

if __name__ == "__main__":
    add_to_startup()
    
    # Start with the default drive
    start_observer(current_drive)
    
    print(f"Watching drive {current_drive}...")
    
    # Icon path (replace with your .ico if desired)
    icon_path = "images.ico"  # If None, a default icon is used
    
    # Start the system tray icon
    systray = SysTrayIcon(
        icon_path,
        f"AutoSorter - {current_drive}",
        create_menu(),
        on_quit=on_quit
    )
    
    systray.start()
import os
import shutil
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from PIL import Image, ImageDraw
import pystray
from plyer import notification
import string

# Biến toàn cục
is_enabled = True
current_drive = "D:\\"
observer = None

# Bản đồ phần mở rộng file
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
    "rar": "Others",
    "zip": "Others",
    "exe": "Programs",
    "msi": "Programs",
    "iso": "DiskImages",
    "img": "DiskImages",
}

# Thiết lập logging
def setup_logging(drive):
    log_dir = os.path.join(drive, "Logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "auto_sorter.log")
    
    # Xóa handlers cũ
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
    """Lấy danh sách các ổ đĩa có sẵn trên hệ thống"""
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives

def move_file(file_path, source):
    """Di chuyển file vào thư mục phù hợp"""
    if os.path.isfile(file_path):
        ext = os.path.splitext(file_path)[1].lower().lstrip(".")
        folder = ext_to_type.get(ext, "Misc")
        dest_path = os.path.join(source, folder)
        os.makedirs(dest_path, exist_ok=True)
        try:
            shutil.move(file_path, os.path.join(dest_path, os.path.basename(file_path)))
            msg = f"File '{os.path.basename(file_path)}' đã được chuyển vào '{folder}'"
            logging.info(msg)
            notification.notify(
                title="AutoSorter",
                message=msg,
                app_name="AutoSorter",
                timeout=3
            )
        except Exception as e:
            logging.error(f"Lỗi khi di chuyển file '{file_path}': {e}")

class Handler(FileSystemEventHandler):
    """Xử lý sự kiện khi có file mới"""
    def __init__(self, source):
        self.source = source
    
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(10)
            msg = f"Phát hiện file mới: {os.path.basename(event.src_path)}"
            logging.info(msg)
            notification.notify(
                title="AutoSorter",
                message=msg,
                app_name="AutoSorter",
                timeout=3
            )
            move_file(event.src_path, self.source)

def create_image():
    """Tạo icon cho system tray"""
    image = Image.new('RGB', (64, 64), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill=(0, 128, 255))
    return image

def start_observer(drive):
    """Khởi động observer cho ổ đĩa được chọn"""
    global observer, current_drive
    
    # Dừng observer cũ nếu có
    if observer and observer.is_alive():
        observer.stop()
        observer.join()
    
    current_drive = drive
    setup_logging(drive)
    
    # Sắp xếp file có sẵn
    for file in os.listdir(drive):
        file_path = os.path.join(drive, file)
        if os.path.isfile(file_path):
            move_file(file_path, drive)
    
    # Khởi động observer mới
    event_handler = Handler(drive)
    observer = Observer()
    observer.schedule(event_handler, drive, recursive=False)
    observer.start()
    
    msg = f"Đang theo dõi ổ đĩa: {drive}"
    logging.info(msg)
    notification.notify(
        title="AutoSorter",
        message=msg,
        app_name="AutoSorter",
        timeout=3
    )

def on_quit(icon, item):
    """Thoát chương trình"""
    icon.stop()
    if observer:
        observer.stop()
    logging.info("Thoát chương trình từ tray icon.")
    os._exit(0)

def on_toggle(icon, item):
    """Bật/tắt tự động sắp xếp"""
    global is_enabled
    is_enabled = not is_enabled
    
    if is_enabled:
        start_observer(current_drive)
        msg = "Đã bật tự động sắp xếp file."
        logging.info(msg)
        notification.notify(
            title="AutoSorter",
            message=msg,
            app_name="AutoSorter",
            timeout=3
        )
    else:
        if observer:
            observer.stop()
        msg = "Đã tắt tự động sắp xếp file."
        logging.info(msg)
        notification.notify(
            title="AutoSorter",
            message=msg,
            app_name="AutoSorter",
            timeout=3
        )
    
    # Cập nhật menu
    icon.menu = create_menu()

def on_select_drive(icon, item, drive):
    """Chọn ổ đĩa mới"""
    global current_drive
    if is_enabled:
        start_observer(drive)
        icon.menu = create_menu()

def create_menu():
    """Tạo menu động với danh sách ổ đĩa"""
    drives = get_available_drives()
    
    # Tạo submenu cho ổ đĩa
    drive_items = []
    for drive in drives:
        checkmark = "✓ " if drive == current_drive else ""
        drive_items.append(
            pystray.MenuItem(
                f"{checkmark}{drive}",
                lambda icon, item, d=drive: on_select_drive(icon, item, d)
            )
        )
    
    toggle_text = "Tắt tự động sắp xếp" if is_enabled else "Bật tự động sắp xếp"
    
    return pystray.Menu(
        pystray.MenuItem(toggle_text, on_toggle),
        pystray.MenuItem("Chọn ổ đĩa", pystray.Menu(*drive_items)),
        pystray.MenuItem("Thoát", on_quit)
    )

def tray_thread():
    """Chạy system tray icon"""
    icon = pystray.Icon("AutoSorter")
    icon.icon = create_image()
    icon.title = f"AutoSorter - {current_drive}"
    icon.menu = create_menu()
    icon.run()

def add_to_startup():
    """Thêm vào startup"""
    try:
        import sys
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
        logging.error(f"Không thể thêm vào startup: {e}")

if __name__ == "__main__":
    add_to_startup()
    
    # Khởi động với ổ đĩa mặc định
    start_observer(current_drive)
    
    print(f"Đang theo dõi ổ đĩa {current_drive}...")
    
    # Chạy tray icon
    threading.Thread(target=tray_thread, daemon=True).start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        if observer:
            observer.stop()
        logging.info("Dừng theo dõi thư mục.")
    
    if observer:
        observer.join()
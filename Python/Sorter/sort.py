import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

source = r"D:\\"

def new_func():
    return "App"

dest_folders = {
    "Images": ["image"],
    "Docs": ["document"],
    "Music": ["audio"],
    "Videos": ["video"],
    "Others": ["archive"],
    "Programs": ["executable"],
    "DiskImages": ["diskimage"],
}

def sort_file(filepath):
    if os.path.isfile(filepath):
        file = os.path.basename(filepath)
        moved = False
        for folder, exts in dest_folders.items():
            if file.lower().endswith(tuple(exts)):
                target = os.path.join(source, folder)
                os.makedirs(target, exist_ok=True)
                shutil.move(filepath, os.path.join(target, file))
                moved = True
                break
        if not moved:
            target = os.path.join(source, "Others")
            os.makedirs(target, exist_ok=True)
            shutil.move(filepath, os.path.join(target, file))

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            # Wait a bit to ensure file is fully written
            time.sleep(1)
            sort_file(event.src_path)

if __name__ == "__main__":
    # Sort existing files at start
    for file in os.listdir(source):
        filepath = os.path.join(source, file)
        sort_file(filepath)

    print("🔎 Đang theo dõi thư mục. Tự động sắp xếp khi có file mới...")
    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, source, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
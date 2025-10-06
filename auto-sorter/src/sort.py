import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

source = r"D:\\"

dest_folders = {
    "Images": [".png", ".jpg", ".jpeg", ".gif"],
    "Docs": [".pdf", ".docx", ".txt", ".xlsx"],
    "Music": [".mp3", ".wav"],
    "Videos": [".mp4", ".mkv", ".avi"],
    "Others": [".rar", ".zip"],
    "Apps": [".exe", ".msi"],
    "DiskImages": [".iso", ".img"],
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
            time.sleep(1)
            sort_file(event.src_path)

if __name__ == "__main__":
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
import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .mover import move_file
from plyer import notification

class Handler(FileSystemEventHandler):
    """Handle events when new files are created"""
    def __init__(self, source):
        self.source = source
    
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(10)  # Delay to ensure the file is fully created
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
    observer = Observer()
    event_handler = Handler(drive)
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
    
    return observer
import os
import shutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:
    def __init__(self, directory, sorter):
        self.directory = directory
        self.sorter = sorter
        self.observer = Observer()

    def run(self):
        event_handler = Handler(self.sorter)
        self.observer.schedule(event_handler, self.directory, recursive=True)
        self.observer.start()
        logging.info(f"Started watching directory: {self.directory}")

        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    def __init__(self, sorter):
        self.sorter = sorter

    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"Detected new file: {event.src_path}")
            self.sorter.sort_file(event.src_path)

def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )
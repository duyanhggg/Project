import os
import logging
from autosorter.watcher import start_observer
from autosorter.config import current_drive, setup_logging

def main():
    setup_logging(current_drive)
    logging.info(f"Starting AutoSorter on drive: {current_drive}")
    
    # Start monitoring the specified drive
    start_observer(current_drive)

if __name__ == "__main__":
    main()
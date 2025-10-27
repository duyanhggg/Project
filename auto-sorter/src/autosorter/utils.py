def setup_logging(drive):
    import os
    import logging
    
    log_dir = os.path.join(drive, "Logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "auto_sorter.log")
    
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
    import string
    import os
    
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\" 
        if os.path.exists(drive):
            drives.append(drive)
    return drives
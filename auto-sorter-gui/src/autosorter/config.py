import os

class Config:
    def __init__(self):
        self.default_directory = os.path.expanduser("~")  # Default to user's home directory
        self.log_file = os.path.join(self.default_directory, "auto_sorter.log")
        self.extensions_map = {
            "Images": [".png", ".jpg", ".jpeg", ".gif"],
            "Docs": [".pdf", ".docx", ".txt", ".xlsx"],
            "Music": [".mp3", ".wav"],
            "Videos": [".mp4", ".mkv", ".avi"],
            "Others": [".rar", ".zip", ".exe", ".msi"],
            "DiskImages": [".iso", ".img"],
        }
        self.logging_enabled = True

    def get_log_file(self):
        return self.log_file

    def is_logging_enabled(self):
        return self.logging_enabled

    def get_extensions_map(self):
        return self.extensions_map

    def set_default_directory(self, directory):
        self.default_directory = directory

    def set_logging_enabled(self, enabled):
        self.logging_enabled = enabled
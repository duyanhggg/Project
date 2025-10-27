def sort_files_by_extension(source_directory, destination_directory):
    import os
    import shutil

    ext_to_folder = {
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

    for filename in os.listdir(source_directory):
        file_path = os.path.join(source_directory, filename)
        if os.path.isfile(file_path):
            ext = os.path.splitext(filename)[1].lower().lstrip(".")
            folder_name = ext_to_folder.get(ext, "Misc")
            dest_folder = os.path.join(destination_directory, folder_name)
            os.makedirs(dest_folder, exist_ok=True)
            shutil.move(file_path, os.path.join(dest_folder, filename))
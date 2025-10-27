def move_file(file_path, source, ext_to_type):
    """Move the file to the appropriate folder based on its extension."""
    if os.path.isfile(file_path):
        ext = os.path.splitext(file_path)[1].lower().lstrip(".")
        folder = ext_to_type.get(ext, "Misc")
        dest_path = os.path.join(source, folder)
        os.makedirs(dest_path, exist_ok=True)
        try:
            shutil.move(file_path, os.path.join(dest_path, os.path.basename(file_path)))
            return f"File '{os.path.basename(file_path)}' moved to '{folder}'"
        except Exception as e:
            return f"Error moving file '{file_path}': {e}"

def sort_files_in_directory(directory, ext_to_type):
    """Sort all files in the specified directory."""
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        move_file(file_path, directory, ext_to_type)
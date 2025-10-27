def read_file(file_path):
    """Read the contents of a file and return it."""
    with open(file_path, 'r') as file:
        return file.read()

def write_file(file_path, content):
    """Write content to a file."""
    with open(file_path, 'w') as file:
        file.write(content)

def log_message(message, log_file='application.log'):
    """Log a message to a specified log file."""
    with open(log_file, 'a') as file:
        file.write(f"{message}\n")

def get_file_extension(file_name):
    """Return the file extension for a given file name."""
    return file_name.split('.')[-1] if '.' in file_name else None

def create_directory(directory):
    """Create a directory if it does not exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
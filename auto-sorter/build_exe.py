import os
import sys
import subprocess

def build_executable():
    """Build the executable for the AutoSorter application."""
    try:
        # Define the command to build the executable
        command = [
            'pyinstaller',
            '--onefile',
            '--windowed',  # Use windowed mode for GUI applications
            'src/autosorter/main.py',  # Entry point of the application
            '--distpath', 'dist',  # Output directory for the executable
            '--workpath', 'build',  # Temporary build directory
            '--specpath', 'build'  # Directory for the .spec file
        ]
        
        # Run the command
        subprocess.run(command, check=True)
        print("Executable built successfully.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()
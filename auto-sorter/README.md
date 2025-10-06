# Auto Sorter Project

## Overview
The Auto Sorter project is designed to automatically organize files in a specified directory based on their file extensions. It utilizes the `watchdog` library to monitor the directory for new files and sorts them into designated folders such as Images, Docs, Music, Videos, and more.

## Features
- Monitors a specified directory for new files.
- Automatically sorts files into folders based on their extensions.
- Supports various file types including images, documents, music, videos, and applications.

## Installation
1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies by running:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the `src/sort.py` script to start monitoring the specified directory.
2. To ensure the script runs automatically on system startup, execute the `setup/windows_startup.bat` file. This will create a shortcut in the Windows startup folder.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
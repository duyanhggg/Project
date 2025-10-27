# Auto Sorter

Auto Sorter is a Python application designed to automatically organize files into designated folders based on their file types. It monitors specified drives for new files and sorts them into appropriate directories, enhancing file management efficiency.

## Features

- **Automatic File Sorting**: Automatically moves files to designated folders based on their extensions.
- **System Tray Integration**: Runs in the background with a system tray icon for easy access and control.
- **Drive Monitoring**: Monitors specified drives for new files and sorts them in real-time.
- **Customizable Settings**: Easily configurable file type mappings and default drive settings.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/auto-sorter.git
   ```
2. Navigate to the project directory:
   ```
   cd auto-sorter
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python src/autosorter/main.py
   ```
2. The application will start monitoring the default drive for new files.
3. Use the system tray icon to enable/disable automatic sorting or select a different drive.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
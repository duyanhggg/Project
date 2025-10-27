# Usage Instructions for AutoSorter

## Overview
AutoSorter is an automatic file sorting application that organizes files into designated folders based on their file types. It monitors a specified drive for new files and moves them to appropriate directories automatically.

## Features
- Automatically sorts files into folders such as Images, Docs, Music, Videos, and more.
- Monitors a selected drive for new file creation.
- System tray integration for easy access and control.
- Configurable file type mappings and default drive settings.

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
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
1. **Run the Application**:
   Execute the main script to start the application:
   ```
   python src/autosorter/main.py
   ```

2. **Select Drive**:
   - Right-click the system tray icon to open the menu.
   - Choose "Select drive" to specify the drive you want to monitor.

3. **Enable/Disable Automatic Sorting**:
   - Use the system tray menu to toggle automatic sorting on or off.

4. **File Sorting**:
   - New files created in the monitored drive will be automatically sorted into their respective folders based on their extensions.

## Configuration
- The file type mappings can be modified in `src/autosorter/config.py`.
- The default drive can also be set in the same configuration file.

## Troubleshooting
- Ensure that the required packages are installed.
- Check the logs in the `Logs` directory on the monitored drive for any errors or issues.

## Contribution
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
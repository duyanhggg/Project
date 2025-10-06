# Auto Sorter Project Setup Instructions

## Overview
The Auto Sorter project automatically organizes files in a specified directory based on their extensions. It uses the `watchdog` library to monitor the directory for new files and sorts them into designated folders such as Images, Docs, Music, Videos, and more.

## Setup Instructions

1. **Clone the Repository**
   Clone the repository to your local machine using:
   ```
   git clone <repository-url>
   ```

2. **Install Dependencies**
   Navigate to the project directory and install the required dependencies using:
   ```
   pip install -r requirements.txt
   ```

3. **Configure the Source Directory**
   Open `src/sort.py` and set the `source` variable to the directory you want to monitor for new files.

4. **Set Up Automatic Startup**
   To ensure that the sorting script runs automatically when your system starts, follow these steps:
   - Run the `windows_startup.bat` file located in the `setup` directory. This will create a shortcut to the script in your Windows startup folder.

5. **Running the Script**
   After setting up the startup, the script will automatically run when you log into your Windows account. You can also run it manually by executing `src/sort.py` in your terminal.

## Notes
- Ensure that the `watchdog` library is installed as it is essential for the functionality of the script.
- You can modify the destination folders and file types in the `dest_folders` dictionary within `src/sort.py` as per your requirements.
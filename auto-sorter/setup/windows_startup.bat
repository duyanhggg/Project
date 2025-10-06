@echo off
set PYTHON_SCRIPT_PATH="C:\path\to\your\project\src\sort.py"
set STARTUP_FOLDER="%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

rem Create a shortcut in the Windows startup folder
powershell "$s=(New-Object -COMObject WScript.Shell).CreateShortcut('%STARTUP_FOLDER%\AutoSorter.lnk');$s.TargetPath=%PYTHON_SCRIPT_PATH%;$s.Save()"
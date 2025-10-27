# Auto tools GUI

This folder contains two GUI wrappers for local automation tools in this workspace:

- `gui_app.py` — AutoSorter GUI for file sorting on a drive (uses `file.pyw`).
- `update_gui.py` — GitHub Auto Upload GUI that wraps `Updatefile.py`.

Added helpers:

- `run_gui_app.pyw` and `run_update_gui.pyw` — launchers that start the GUIs using `pythonw` (no console window on Windows).
- `create_shortcut.py` — helper to create a Windows shortcut (.lnk) in the current user's Startup folder.

Quick start (Windows PowerShell):

1. Install dependencies (see `requirements.txt`):

   python -m pip install -r requirements.txt

2. Run the GUI (console visible):

   python .\update_gui.py

   or run without console (if pythonw is available):

   pythonw .\run_update_gui.pyw

3. To auto-start on login, use the `create_shortcut.py` utility to create a shortcut in your Startup folder. Example:

   python .\create_shortcut.py --target "C:\\Python\\pythonw.exe" --script "e:\\Code\\Python\\run_update_gui.pyw" --name "GitHub Auto Upload"

Notes:
- Background/daemon features rely on spawned processes and are not Windows services.
- Check the logs under your home directory as described in the GUI.

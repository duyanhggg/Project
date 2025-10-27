# Usage & Tray behavior

This document explains the tray behavior when running the GitHub Auto Upload tool in background mode.

When you start the tool in background mode (from the GUI 'Start Background' button or by launching
`Updatefile.py --run-background`), the detached process will attempt to show a system tray icon on Windows.

Tray menu options

- Open GUI — launches the GUI using `pythonw` so no console window appears.
- Stop background — requests the background process to stop gracefully and removes the tray icon.

Troubleshooting

- If the tray icon does not appear, ensure `infi.systray` is installed in the Python environment used by the background process.
- Check the background PID file located in your home directory (e.g., `~/.github_uploader_bg.json`) to confirm the process is running.

Notes

- The tray integration is attempted only on Windows. On other platforms the background process runs headless.
- The background process is not a Windows Service. It runs under your user session and will stop on logout/shutdown unless managed by a service manager or scheduler.

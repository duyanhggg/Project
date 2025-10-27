import threading
import time
import os
import importlib
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Simple GUI wrapper for the script in file.pyw
# Features: select drive, start/stop monitoring, enable/disable, view tail of log, add to startup


def safe_import_autoscript():
    try:
        autos = importlib.import_module('file')
        return autos
    except Exception as e:
        raise ImportError(f"Cannot import the autosorter script 'file.pyw': {e}")


class AutoSorterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('AutoSorter GUI')
        self.geometry('700x420')

        try:
            self.autos = safe_import_autoscript()
        except Exception as e:
            messagebox.showerror('Import error', str(e))
            self.destroy()
            return

        # Drive selection
        drives = self.autos.get_available_drives()
        self.selected_drive = tk.StringVar(value=self.autos.current_drive if self.autos.current_drive in drives else (drives[0] if drives else ''))

        frame = ttk.Frame(self, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text='Select drive:').grid(column=0, row=0, sticky=tk.W)
        self.drive_combo = ttk.Combobox(frame, values=drives, textvariable=self.selected_drive, state='readonly', width=12)
        self.drive_combo.grid(column=1, row=0, sticky=tk.W)

        self.start_btn = ttk.Button(frame, text='Start Monitoring', command=self.start_monitor)
        self.start_btn.grid(column=2, row=0, padx=8)

        self.stop_btn = ttk.Button(frame, text='Stop Monitoring', command=self.stop_monitor, state=tk.DISABLED)
        self.stop_btn.grid(column=3, row=0)

        # Enable/disable toggle
        self.enabled_var = tk.BooleanVar(value=self.autos.is_enabled)
        self.enable_check = ttk.Checkbutton(frame, text='Automatic sorting enabled', variable=self.enabled_var, command=self.toggle_enabled)
        self.enable_check.grid(column=0, row=1, columnspan=2, sticky=tk.W, pady=(6, 0))

        # Add to startup
        ttk.Button(frame, text='Add to startup', command=self.add_startup).grid(column=2, row=1, padx=8)

        # Run hidden / stop hidden (run the autosorter in background without showing a console window)
        self.hidden_run_btn = ttk.Button(frame, text='Run Hidden (background)', command=self.run_hidden)
        self.hidden_run_btn.grid(column=3, row=1, padx=(8, 0))

        self.hidden_stop_btn = ttk.Button(frame, text='Stop Hidden', command=self.stop_hidden, state=tk.DISABLED)
        self.hidden_stop_btn.grid(column=4, row=1)

        # Help / Instructions
        ttk.Button(frame, text='Help / Instructions', command=self.show_help).grid(column=0, row=5, columnspan=4, sticky=tk.W, pady=(8, 0))

        # Log viewer
        ttk.Label(frame, text='Recent logs:').grid(column=0, row=2, sticky=tk.W, pady=(10, 0))
        self.log_text = scrolledtext.ScrolledText(frame, height=15, width=90, state=tk.DISABLED)
        self.log_text.grid(column=0, row=3, columnspan=4, pady=(4, 0))

        # Status line
        self.status_var = tk.StringVar(value='Idle')
        ttk.Label(frame, textvariable=self.status_var).grid(column=0, row=4, columnspan=4, sticky=tk.W, pady=(6, 0))

        # Internal
        self.monitor_thread = None
        self._stop_thread = threading.Event()
        self.hidden_proc = None

        # Periodically refresh list of drives and logs
        self.after(2000, self.periodic_refresh)

    def start_monitor(self):
        drive = self.selected_drive.get()
        if not drive or not os.path.exists(drive):
            messagebox.showerror('Drive error', 'Please select a valid drive.')
            return

        # Start in background thread to avoid blocking UI (initial sorting can take time)
        def target():
            try:
                self.status_var.set(f'Starting monitor on {drive}...')
                self.autos.start_observer(drive)
                self.status_var.set(f'Monitoring: {drive}')
            except Exception as e:
                messagebox.showerror('Error', f'Error starting observer: {e}')
                self.status_var.set('Error')

        self.monitor_thread = threading.Thread(target=target, daemon=True)
        self.monitor_thread.start()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

    def stop_monitor(self):
        # Stop observer if exists
        try:
            if self.autos.observer:
                self.autos.observer.stop()
                self.autos.observer.join(timeout=2)
            self.status_var.set('Stopped')
        except Exception as e:
            messagebox.showwarning('Warning', f'Problem stopping observer: {e}')

        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def toggle_enabled(self):
        # Use the script's existing toggle function (it expects a systray param but doesn't require it)
        try:
            # Call on_toggle with None - it will flip global is_enabled and update state
            self.autos.on_toggle(None)
            self.enabled_var.set(self.autos.is_enabled)
            self.status_var.set('Enabled' if self.autos.is_enabled else 'Disabled')
        except Exception as e:
            messagebox.showerror('Error', f'Cannot toggle enabled state: {e}')

    def add_startup(self):
        try:
            self.autos.add_to_startup()
            messagebox.showinfo('Startup', 'Attempted to add to startup (check logs for errors).')
        except Exception as e:
            messagebox.showerror('Error', f'Cannot add to startup: {e}')

    def _find_autoscript_path(self):
        # Try to locate the autosorter script in the same folder
        base = os.path.dirname(os.path.abspath(__file__))
        candidates = [os.path.join(base, 'file.pyw'), os.path.join(base, 'file.py')]
        for c in candidates:
            if os.path.exists(c):
                return c
        # fallback to module file if imported
        try:
            return os.path.abspath(self.autos.__file__)
        except Exception:
            return None

    def run_hidden(self):
        """Start the autosorter as a separate hidden/background process (no console window)."""
        if self.hidden_proc and self.hidden_proc.poll() is None:
            messagebox.showinfo('Hidden runner', 'Hidden process already running.')
            return

        script_path = self._find_autoscript_path()
        if not script_path:
            messagebox.showerror('Error', 'Cannot find the autosorter script to run hidden.')
            return

        # Prefer pythonw on Windows to avoid a console. If not available, use STARTUPINFO/SW_HIDE or CREATE_NO_WINDOW.
        exe = sys.executable
        if sys.platform.startswith('win') and exe.lower().endswith('python.exe'):
            maybe = exe[:-10] + 'pythonw.exe'
            if os.path.exists(maybe):
                exe = maybe

        creationflags = 0
        startupinfo = None
        try:
            if os.name == 'nt':
                # CREATE_NO_WINDOW is the simplest if available
                creationflags = subprocess.CREATE_NO_WINDOW
        except Exception:
            # fallback to STARTUPINFO
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            except Exception:
                startupinfo = None

        try:
            self.hidden_proc = subprocess.Popen([exe, script_path], creationflags=creationflags, startupinfo=startupinfo, close_fds=True)
            self.hidden_run_btn.config(state=tk.DISABLED)
            self.hidden_stop_btn.config(state=tk.NORMAL)
            self.status_var.set(f'Hidden process started (pid={self.hidden_proc.pid})')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to start hidden process: {e}')

    def stop_hidden(self):
        if not self.hidden_proc:
            messagebox.showinfo('Stop hidden', 'No hidden process to stop.')
            return
        try:
            if self.hidden_proc.poll() is None:
                self.hidden_proc.terminate()
                self.hidden_proc.wait(timeout=5)
            self.status_var.set('Hidden process stopped')
        except Exception as e:
            messagebox.showwarning('Warning', f'Could not stop hidden process cleanly: {e}')
        finally:
            self.hidden_proc = None
            self.hidden_run_btn.config(state=tk.NORMAL)
            self.hidden_stop_btn.config(state=tk.DISABLED)

    def show_help(self):
        help_text = (
            "AutoSorter GUI - Instructions\n\n"
            "1) Select a drive and click 'Start Monitoring' to start the watcher in this GUI.\n"
            "2) 'Run Hidden (background)' launches the autosorter script as a separate process without showing a console window.\n"
            "   - This uses pythonw.exe when available, or hides the window via the Windows API.\n"
            "3) Use 'Stop Hidden' to terminate the background hidden process.\n"
            "4) 'Add to startup' will attempt to create a shortcut in your Windows startup folder so the autosorter runs at login.\n"
            "5) Logs are stored at <DRIVE>\\Logs\\auto_sorter.log (the GUI shows the tail).\n\n"
            "Notes:\n"
            "- If you double-click to run a script without console, use the .pyw variant or the Run Hidden button.\n"
            "- On Windows, running as hidden does not make the process a service; it still runs under your user session.\n"
        )
        messagebox.showinfo('Help / Instructions', help_text)

    def tail_log(self, path, n=200):
        if not os.path.exists(path):
            return ''
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            return ''.join(lines[-n:])
        except Exception:
            return ''

    def refresh_logs(self):
        # Determine log path used by the autoscript
        drive = self.selected_drive.get() or self.autos.current_drive
        log_path = os.path.join(drive, 'Logs', 'auto_sorter.log')
        content = self.tail_log(log_path, n=500)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.insert(tk.END, content)
        self.log_text.config(state=tk.DISABLED)

    def refresh_drives(self):
        drives = self.autos.get_available_drives()
        self.drive_combo['values'] = drives
        if self.selected_drive.get() not in drives and drives:
            self.selected_drive.set(drives[0])

    def periodic_refresh(self):
        try:
            self.refresh_drives()
            self.refresh_logs()
        finally:
            self.after(2000, self.periodic_refresh)


def main():
    app = AutoSorterGUI()
    app.mainloop()


if __name__ == '__main__':
    main()

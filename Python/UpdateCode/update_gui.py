import os
import sys
import threading
import time
import importlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


def safe_import_uploader():
    try:
        mod = importlib.import_module('Updatefile')
        return mod
    except Exception as e:
        raise ImportError(f"Cannot import Updatefile.py: {e}")


class UpdateGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('GitHub Auto Upload')
        self.geometry('820x600')

        try:
            self.mod = safe_import_uploader()
            self.uploader = self.mod.GitHubUploader()
        except Exception as e:
            messagebox.showerror('Import error', str(e))
            self.destroy()
            return

        # Main frame
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # Repo path
        ttk.Label(frm, text='Repository folder:').grid(column=0, row=0, sticky=tk.W)
        self.repo_var = tk.StringVar(value=self.uploader.repo_path or '')
        self.repo_entry = ttk.Entry(frm, textvariable=self.repo_var, width=68)
        self.repo_entry.grid(column=1, row=0, columnspan=3, sticky=tk.W)
        ttk.Button(frm, text='Browse', command=self.browse_repo).grid(column=4, row=0, padx=6)

        # Repo URL
        ttk.Label(frm, text='Repository URL:').grid(column=0, row=1, sticky=tk.W, pady=(6, 0))
        self.url_var = tk.StringVar(value=self.uploader.repo_url or '')
        self.url_entry = ttk.Entry(frm, textvariable=self.url_var, width=68)
        self.url_entry.grid(column=1, row=1, columnspan=3, sticky=tk.W, pady=(6, 0))

        # Branch
        ttk.Label(frm, text='Branch:').grid(column=0, row=2, sticky=tk.W, pady=(6, 0))
        self.branch_var = tk.StringVar(value=self.uploader.branch or 'main')
        self.branch_entry = ttk.Entry(frm, textvariable=self.branch_var, width=20)
        self.branch_entry.grid(column=1, row=2, sticky=tk.W, pady=(6, 0))

        # Commit prefix
        ttk.Label(frm, text='Commit message prefix:').grid(column=2, row=2, sticky=tk.W, pady=(6, 0))
        self.prefix_var = tk.StringVar(value=self.uploader.auto_upload_prefix or 'Auto update')
        self.prefix_entry = ttk.Entry(frm, textvariable=self.prefix_var, width=28)
        self.prefix_entry.grid(column=3, row=2, sticky=tk.W, pady=(6, 0))

        # Buttons row 1
        ttk.Button(frm, text='Load config', command=self.load_config).grid(column=0, row=3, pady=(10, 0), sticky=tk.W)
        ttk.Button(frm, text='Save config', command=self.save_config).grid(column=1, row=3, pady=(10, 0), sticky=tk.W)
        ttk.Button(frm, text='Reset config', command=self.reset_config).grid(column=2, row=3, pady=(10, 0), sticky=tk.W)
        ttk.Button(frm, text='Upload Now', command=self.upload_now).grid(column=3, row=3, pady=(10, 0))
        ttk.Button(frm, text='Show Logs', command=self.open_logs).grid(column=4, row=3, pady=(10, 0))

        # Buttons row 2 (background)
        ttk.Separator(frm, orient=tk.HORIZONTAL).grid(column=0, row=4, columnspan=5, sticky='ew', pady=8)
        ttk.Label(frm, text='Background auto-upload (detached) settings:').grid(column=0, row=5, columnspan=3, sticky=tk.W)

        ttk.Label(frm, text='Interval (minutes):').grid(column=0, row=6, sticky=tk.W, pady=(6, 0))
        self.interval_var = tk.IntVar(value=self.uploader.auto_upload_interval or 10)
        self.interval_spin = ttk.Spinbox(frm, from_=1, to=1440, textvariable=self.interval_var, width=8)
        self.interval_spin.grid(column=1, row=6, sticky=tk.W, pady=(6, 0))

        ttk.Button(frm, text='Start Background', command=self.start_background).grid(column=2, row=6, padx=6, pady=(6, 0))
        ttk.Button(frm, text='Stop Background', command=self.stop_background).grid(column=3, row=6, pady=(6, 0))
        ttk.Button(frm, text='Status', command=self.show_bg_status).grid(column=4, row=6, pady=(6, 0))

        # Status indicator
        ttk.Label(frm, text='Status:').grid(column=0, row=7, sticky=tk.W, pady=(6, 0))
        self.status_label = ttk.Label(frm, text='[CHECKING] Initializing...', foreground='blue')
        self.status_label.grid(column=1, row=7, sticky=tk.W, pady=(6, 0))
        ttk.Button(frm, text='Refresh Status', command=self.refresh_status).grid(column=2, row=7, pady=(6, 0))

        # Log viewer
        ttk.Label(frm, text='Recent log (tail):').grid(column=0, row=8, sticky=tk.W, pady=(12, 0))
        self.log_text = scrolledtext.ScrolledText(frm, width=100, height=20)
        self.log_text.grid(column=0, row=9, columnspan=5, pady=(6, 0))

        # Help
        ttk.Button(frm, text='Help / Instructions', command=self.show_help).grid(column=0, row=10, pady=(10, 0), sticky=tk.W)

        # Periodic refresh
        self.after(1500, self.refresh_tail)
        # Initial status check
        self.after(500, self.refresh_status)

    def browse_repo(self):
        d = filedialog.askdirectory(title='Select repository folder')
        if d:
            self.repo_var.set(d)

    def save_config(self):
        self.uploader.repo_path = self.repo_var.get().strip() or None
        self.uploader.repo_url = self.url_var.get().strip() or None
        self.uploader.branch = self.branch_var.get().strip() or 'main'
        self.uploader.auto_upload_prefix = self.prefix_var.get().strip() or 'Auto update'
        self.uploader.auto_upload_interval = int(self.interval_var.get() or 10)

        # Save into uploader.config under 'gui' name
        try:
            self.uploader.config['gui_saved'] = {
                'path': self.uploader.repo_path,
                'url': self.uploader.repo_url,
                'branch': self.uploader.branch,
                'interval': self.uploader.auto_upload_interval,
                'prefix': self.uploader.auto_upload_prefix,
            }
            self.uploader.save_config()
            messagebox.showinfo('Saved', 'Configuration saved to disk')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save config: {e}')

    def load_config(self):
        """Load the saved GUI config (key 'gui_saved') from uploader.config and populate fields."""
        try:
            cfg = self.uploader.config.get('gui_saved') if isinstance(self.uploader.config, dict) else None
            if not cfg:
                messagebox.showinfo('Load config', 'No saved GUI configuration found.')
                return
            self.repo_var.set(cfg.get('path') or '')
            self.url_var.set(cfg.get('url') or '')
            self.branch_var.set(cfg.get('branch') or 'main')
            self.interval_var.set(cfg.get('interval') or 10)
            self.prefix_var.set(cfg.get('prefix') or 'Auto update')
            # Also update uploader in-memory
            self.uploader.repo_path = self.repo_var.get().strip() or None
            self.uploader.repo_url = self.url_var.get().strip() or None
            self.uploader.branch = self.branch_var.get().strip() or 'main'
            self.uploader.auto_upload_interval = int(self.interval_var.get() or 10)
            self.uploader.auto_upload_prefix = self.prefix_var.get().strip() or 'Auto update'
            messagebox.showinfo('Load config', 'Configuration loaded into the GUI.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load config: {e}')

    def reset_config(self):
        """Remove saved GUI config from uploader.config (reset to defaults)."""
        try:
            ok = messagebox.askyesno('Reset config', 'Are you sure you want to remove the saved GUI configuration?')
            if not ok:
                return
            if isinstance(self.uploader.config, dict) and 'gui_saved' in self.uploader.config:
                del self.uploader.config['gui_saved']
                self.uploader.save_config()
            # Clear GUI fields
            self.repo_var.set('')
            self.url_var.set('')
            self.branch_var.set('main')
            self.interval_var.set(10)
            self.prefix_var.set('Auto update')
            # Update uploader memory
            self.uploader.repo_path = None
            self.uploader.repo_url = None
            self.uploader.branch = 'main'
            self.uploader.auto_upload_interval = None
            self.uploader.auto_upload_prefix = None
            messagebox.showinfo('Reset config', 'Saved configuration removed and GUI reset.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to reset config: {e}')

    def upload_now(self):
        # Run a non-interactive upload using current fields
        repo = self.repo_var.get().strip() or os.getcwd()
        url = self.url_var.get().strip()
        branch = self.branch_var.get().strip() or 'main'
        commit_prefix = self.prefix_var.get().strip() or 'Auto update'

        if not os.path.exists(repo):
            messagebox.showerror('Error', 'Repository folder does not exist')
            return
        if not url:
            messagebox.showerror('Error', 'Repository URL is required')
            return

        def worker():
            try:
                self.log('Starting upload...')
                self.uploader.repo_path = repo
                self.uploader.repo_url = url
                self.uploader.branch = branch

                if not self.uploader.init_git_repo():
                    self.log('init_git_repo failed')
                    return
                if not self.uploader.configure_remote():
                    self.log('configure_remote failed')
                    return

                self.uploader.show_git_status()
                if not self.uploader.git_add_all():
                    self.log('git add failed')
                    return

                commit_msg = f"{commit_prefix} {time.strftime('%Y-%m-%d %H:%M:%S')}"
                if not self.uploader.git_commit(commit_msg):
                    self.log('git commit failed or nothing to commit')
                if not self.uploader.git_push():
                    self.log('git push failed')
                else:
                    self.log('Upload complete')
                # refresh log
                self.refresh_tail()
            except Exception as e:
                messagebox.showerror('Error', f'Upload failed: {e}')

        threading.Thread(target=worker, daemon=True).start()

    def start_background(self):
        self.uploader.repo_path = self.repo_var.get().strip() or None
        self.uploader.repo_url = self.url_var.get().strip() or None
        self.uploader.auto_upload_interval = int(self.interval_var.get() or 10)
        self.uploader.auto_upload_prefix = self.prefix_var.get().strip() or 'Auto update'

        def bg_worker():
            ok = self.uploader.start_background_mode()
            messagebox.showinfo('Background', f'Start background: {ok}')
            self.refresh_tail()
            self.refresh_status()  # Update status display

        threading.Thread(target=bg_worker, daemon=True).start()

    def stop_background(self):
        def bg_stop():
            ok = self.uploader.stop_background_mode()
            messagebox.showinfo('Background', f'Stop background: {ok}')
            self.refresh_tail()
            self.refresh_status()  # Update status display
        threading.Thread(target=bg_stop, daemon=True).start()

    def refresh_status(self):
        """Update the status label with current background process status"""
        try:
            pid = self.uploader._read_bg_pid()
            status = self.uploader._read_bg_status() or {}
            running = self.uploader._is_process_running(pid)
            
            if running:
                self.status_label.config(text='[RUNNING] Background process is active', foreground='green')
            else:
                self.status_label.config(text='[STOPPED] Background process is not running', foreground='red')
                
            # Update status every 5 seconds
            self.after(5000, self.refresh_status)
        except Exception as e:
            self.status_label.config(text=f'[ERROR] Error checking status: {e}', foreground='red')
            self.after(10000, self.refresh_status)  # Retry in 10 seconds on error

    def show_bg_status(self):
        """Show detailed background status in a dialog"""
        try:
            pid = self.uploader._read_bg_pid()
            status = self.uploader._read_bg_status() or {}
            running = self.uploader._is_process_running(pid)
            
            # Format status information
            status_text = f"Background Process Status\n{'='*30}\n\n"
            status_text += f"Process ID: {pid if pid else 'Not found'}\n"
            status_text += f"Running: {'Yes' if running else 'No'}\n"
            
            if status:
                status_text += f"\nLast Activity:\n"
                if status.get('timestamp'):
                    status_text += f"  Time: {status['timestamp']}\n"
                if status.get('result'):
                    result = status['result']
                    result_icon = '[OK]' if result.lower() == 'success' else '[FAIL]' if result.lower() == 'failure' else '[WAIT]'
                    status_text += f"  Result: {result_icon} {result}\n"
                if status.get('message'):
                    status_text += f"  Message: {status['message']}\n"
                if status.get('interval'):
                    status_text += f"  Interval: {status['interval']} minutes\n"
                if status.get('path'):
                    status_text += f"  Repository: {status['path']}\n"
                if status.get('branch'):
                    status_text += f"  Branch: {status['branch']}\n"
            else:
                status_text += "\nNo status information available"
                
            messagebox.showinfo('Detailed Background Status', status_text)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to get status: {e}')

    def open_logs(self):
        path = self.uploader.log_dir
        if not os.path.exists(path):
            messagebox.showinfo('Logs', 'No logs folder yet')
            return
        try:
            if os.name == 'nt':
                os.startfile(path)
            elif sys.platform == 'darwin':
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
        except Exception as e:
            messagebox.showerror('Error', f'Cannot open logs: {e}')

    def refresh_tail(self):
        # show tail of latest log file
        try:
            logs = sorted([f for f in os.listdir(self.uploader.log_dir) if f.endswith('.log')], reverse=True)
            if not logs:
                self.log_text.delete('1.0', tk.END)
                self.log_text.insert(tk.END, 'No logs yet')
            else:
                latest = os.path.join(self.uploader.log_dir, logs[0])
                with open(latest, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[-400:]
                self.log_text.delete('1.0', tk.END)
                self.log_text.insert(tk.END, ''.join(lines))
        except Exception:
            pass
        finally:
            self.after(2000, self.refresh_tail)

    def log(self, msg):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        self.log_text.insert(tk.END, f'[{now}] {msg}\n')
        self.log_text.see(tk.END)

    def show_help(self):
        help_text = (
            "This GUI controls the GitHub Auto Upload tool.\n\n"
            "- Fill repository folder and URL.\n"
            "- 'Upload Now' runs a non-interactive upload (git add/commit/push).\n"
            "- 'Start Background' starts the tool detached (uses the tool's background mode).\n"
            "- 'Stop Background' stops the detached background process.\n"
            "- Logs are stored under the user's.home/.github_uploader_logs folder.\n"
            "\nNote: Background mode runs as a separate process and will continue after you close this GUI."
        )
        messagebox.showinfo('Help', help_text)


def main():
    app = UpdateGUI()
    app.mainloop()


if __name__ == '__main__':
    main()

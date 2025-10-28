#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Auto Upload Tool Pro
Công cụ tự động đẩy code lên GitHub với nhiều tính năng nâng cao
"""

import os
import subprocess
import sys
import json
import time
import threading
import logging
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import simpledialog


class GitHubUploader:
    def __init__(self):
        # Default to current working directory; can be adjusted later
        self.repo_path = os.getcwd()
        self.repo_url = None
        self.branch = "main"
        self.auto_upload_interval = 10  # minutes
        self.auto_upload_prefix = "Auto update"
        self._auto_thread = None
        self._auto_stop = threading.Event()
        # Config file
        self.config_path = os.path.join(Path.home(), ".github_uploader_config.json")
        # Logs
        self.log_dir = os.path.join(Path.home(), ".github_uploader_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.logger = logging.getLogger("github_uploader")
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            fh = logging.FileHandler(os.path.join(self.log_dir, "uploader.log"), encoding='utf-8')
            fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            fh.setFormatter(fmt)
            self.logger.addHandler(fh)
        self.load_config()
        self.logger.info("Uploader initialized")
        # Background process files
        self.bg_pid_file = os.path.join(self.log_dir, "bg.pid")
        self.bg_status_file = os.path.join(self.log_dir, "bg_status.json")

    # ------------- Config persistence -------------
    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.repo_path = data.get("path", self.repo_path)
                self.repo_url = data.get("url", self.repo_url)
                self.branch = data.get("branch", self.branch)
                self.auto_upload_interval = int(data.get("interval", self.auto_upload_interval) or 10)
                self.auto_upload_prefix = data.get("prefix", self.auto_upload_prefix) or "Auto update"
                self._profiles = data.get("profiles", {}) if isinstance(data.get("profiles", {}), dict) else {}
        except Exception:
            # ignore config errors
            pass

    def save_config(self):
        try:
            data = {
                "path": self.repo_path,
                "url": self.repo_url,
                "branch": self.branch,
                "interval": self.auto_upload_interval,
                "prefix": self.auto_upload_prefix,
                "profiles": getattr(self, "_profiles", {}),
            }
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ------------- Saved profiles -------------
    def list_profiles(self):
        return sorted((getattr(self, "_profiles", {}) or {}).keys())

    def get_profile(self, name: str):
        return (getattr(self, "_profiles", {}) or {}).get(name)

    def save_profile(self, name: str, profile: dict = None):
        if not hasattr(self, "_profiles") or not isinstance(self._profiles, dict):
            self._profiles = {}
        if profile is None:
            profile = {
                "path": self.repo_path,
                "url": self.repo_url,
                "branch": self.branch,
                "interval": self.auto_upload_interval,
                "prefix": self.auto_upload_prefix,
            }
        self._profiles[name] = profile
        self.save_config()

    def delete_profile(self, name: str):
        if hasattr(self, "_profiles") and isinstance(self._profiles, dict) and name in self._profiles:
            del self._profiles[name]
            self.save_config()
            return True
        return False
    
    def load_profile(self, name: str) -> bool:
        prof = self.get_profile(name)
        if not prof:
            return False
        self.repo_path = prof.get("path", self.repo_path)
        self.repo_url = prof.get("url", self.repo_url)
        self.branch = prof.get("branch", self.branch)
        self.auto_upload_interval = int(prof.get("interval", self.auto_upload_interval) or 10)
        self.auto_upload_prefix = prof.get("prefix", self.auto_upload_prefix) or "Auto update"
        self.save_config()
        return True

    def run_command(self, command: str):
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
            )
            stdout = (result.stdout or "").strip()
            stderr = (result.stderr or "").strip()
            self.logger.info(f"$ {command}\nstdout: {stdout}\nstderr: {stderr}")
            return result.returncode == 0, stdout, stderr
        except Exception as e:
            self.logger.exception(f"Command failed: {command}")
            return False, "", str(e)

    def _git(self, args: str):
        return self.run_command(f'git -C "{self.repo_path}" {args}')

    def init_git_repo(self) -> bool:
        ok, out, err = self._git("rev-parse --is-inside-work-tree")
        if ok and out.strip() == "true":
            return True
        ok, _, _ = self._git("init")
        return ok

    def configure_remote(self) -> bool:
        self.init_git_repo()
        if not self.repo_url:
            # ask for URL
            try:
                url = simpledialog.askstring("Remote", "Nhập URL Git remote (origin):")
            except Exception:
                url = None
            if not url:
                messagebox.showerror("Remote", "Chưa có URL remote")
                return False
            self.repo_url = url.strip()
        ok, _, _ = self._git("remote get-url origin")
        if ok:
            # update to ensure correct
            self._git(f"remote set-url origin {self.repo_url}")
        else:
            self._git(f"remote add origin {self.repo_url}")
        self.save_config()
        return True

    def show_git_status(self):
        self.init_git_repo()
        ok, out, err = self._git("status -s -b")
        text = out if ok else err or "No output"
        try:
            messagebox.showinfo("Git status", text)
        except Exception:
            print(text)

    def create_gitignore(self):
        self.init_git_repo()
        path = os.path.join(self.repo_path, ".gitignore")
        if not os.path.exists(path):
            content = (
                "__pycache__/\n*.py[cod]\n*.egg-info/\n.env\n.venv/\nvenv/\n"
                "dist/\nbuild/\n*.log\n.idea/\n.vscode/\n"
            )
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        messagebox.showinfo(".gitignore", "Created/updated .gitignore")

    def git_add_all(self) -> bool:
        self.init_git_repo()
        ok, _, _ = self._git("add -A")
        return ok

    def git_commit(self, message: str) -> bool:
        self.init_git_repo()
        ok, out, err = self._git(f"commit -m \"{message}\"")
        # when there's nothing to commit, commit exits non-zero; treat as ok
        if not ok and ("nothing to commit" in (out + err).lower()):
            return True
        return ok

    def git_push(self) -> bool:
        self.init_git_repo()
        # Try to detect default remote
        ok, out, _ = self._git("remote get-url origin")
        if ok:
            self.repo_url = out.strip() or self.repo_url
        if not self.repo_url:
            messagebox.showerror("Git push", "Remote URL not configured (origin).")
            return False
        ok, out, err = self._git(f"push -u origin {self.branch}")
        if not ok:
            messagebox.showerror("Git push", err or out or "Push failed")
        return ok

    # ------------- Background auto-upload (in-process thread) -------------
    def _auto_loop(self):
        while not self._auto_stop.is_set():
            try:
                self.git_add_all()
                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.git_commit(f"{self.auto_upload_prefix} {ts}")
                self.git_push()
            except Exception:
                pass
            # wait minutes in 1-second steps so we can stop promptly
            total = max(1, int(self.auto_upload_interval) * 60)
            for _ in range(total):
                if self._auto_stop.is_set():
                    break
                time.sleep(1)

    def start_background_mode(self) -> bool:
        # Spawn a detached background process that runs --run-background
        if self.is_background_running():
            messagebox.showinfo("Background", "Đã chạy nền")
            return True
        if not self.configure_remote():
            return False
        self.save_config()
        try:
            cmd = f'"{sys.executable}" "{os.path.abspath(__file__)}" --run-background'
            creationflags = 0
            startupinfo = None
            if sys.platform.startswith('win'):
                # CREATE_NO_WINDOW = 0x08000000
                creationflags = 0x08000000
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creationflags, startupinfo=startupinfo)
            # Store PID
            with open(self.bg_pid_file, 'w', encoding='utf-8') as f:
                f.write(str(proc.pid))
            messagebox.showinfo("Background", "Đã bật chạy nền (tiến trình tách biệt)")
            return True
        except Exception as e:
            messagebox.showerror("Background", f"Không thể khởi chạy nền: {e}")
            return False

    def stop_background_mode(self) -> bool:
        pid = self._read_bg_pid()
        if not pid:
            return False
        try:
            if sys.platform.startswith('win'):
                subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                os.kill(pid, 15)
            return True
        except Exception:
            return False

    # -------- Detached background helpers --------
    def _read_bg_pid(self):
        try:
            if os.path.exists(self.bg_pid_file):
                with open(self.bg_pid_file, 'r', encoding='utf-8') as f:
                    return int((f.read() or '').strip() or '0') or None
        except Exception:
            return None
        return None

    def is_background_running(self) -> bool:
        pid = self._read_bg_pid()
        if not pid:
            return False
        try:
            if sys.platform.startswith('win'):
                out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True)
                return str(pid) in out.stdout
            else:
                os.kill(pid, 0)
                return True
        except Exception:
            return False

    def _write_status(self, result: str, message: str = ""):
        try:
            data = {
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "result": result,
                "message": message,
                "path": self.repo_path,
                "branch": self.branch,
                "interval": self.auto_upload_interval,
                "prefix": self.auto_upload_prefix,
            }
            with open(self.bg_status_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def read_status(self):
        try:
            if os.path.exists(self.bg_status_file):
                with open(self.bg_status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            return None
        return None

    # -------- Background loop entrypoint (detached) --------
    def run_background_loop(self):
        # Write own PID
        try:
            with open(self.bg_pid_file, 'w', encoding='utf-8') as f:
                f.write(str(os.getpid()))
        except Exception:
            pass
        self._write_status('start', 'Background loop started')
        while True:
            try:
                self.load_config()  # refresh config if changed
                self.git_add_all()
                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                committed = self.git_commit(f"{self.auto_upload_prefix} {ts}")
                pushed = self.git_push()
                if pushed:
                    self._write_status('success', 'Pushed successfully')
                elif committed:
                    self._write_status('nochange', 'Nothing to push')
                else:
                    self._write_status('nochange', 'Nothing to commit')
            except Exception as e:
                self._write_status('failure', str(e))
            # sleep until next run
            interval_sec = max(60, int(self.auto_upload_interval) * 60)
            time.sleep(interval_sec)

    # Placeholders for menu items not wired into this minimal GUI
    def manage_saved_configs(self):
        try:
            win = tk.Toplevel(self.root)
            win.title("Quản lý cấu hình")
            win.geometry("560x380")
            frm = ttk.Frame(win, padding=12)
            frm.pack(expand=True, fill='both')

            # Profiles list
            left = ttk.Frame(frm)
            left.pack(side='left', fill='y', padx=(0, 12))
            ttk.Label(left, text='Profiles:').pack(anchor='w')
            lb = tk.Listbox(left, height=12)
            lb.pack()

            def refresh_list():
                lb.delete(0, 'end')
                for name in self.uploader.list_profiles():
                    lb.insert('end', name)

            # Edit panel
            right = ttk.Frame(frm)
            right.pack(side='left', expand=True, fill='both')
            e_path = ttk.Entry(right, width=48)
            e_url = ttk.Entry(right, width=48)
            e_branch = ttk.Entry(right, width=20)
            e_interval = ttk.Entry(right, width=10)
            e_prefix = ttk.Entry(right, width=30)

            def grid_row(r, label, widget):
                ttk.Label(right, text=label+':').grid(column=0, row=r, sticky='w', pady=4)
                widget.grid(column=1, row=r, sticky='w')
            grid_row(0, 'Path', e_path)
            grid_row(1, 'URL', e_url)
            grid_row(2, 'Branch', e_branch)
            grid_row(3, 'Interval (m)', e_interval)
            grid_row(4, 'Prefix', e_prefix)

            # Buttons
            btns = ttk.Frame(right)
            btns.grid(column=0, row=5, columnspan=2, pady=10, sticky='w')
            def choose_path():
                p = filedialog.askdirectory(title='Chọn thư mục repository', initialdir=e_path.get() or self.uploader.repo_path)
                if p:
                    e_path.delete(0, 'end'); e_path.insert(0, p)
            ttk.Button(btns, text='Chọn thư mục', command=choose_path).pack(side='left')

            def on_save_as():
                name = simpledialog.askstring('Lưu cấu hình', 'Tên profile:')
                if not name:
                    return
                prof = {
                    'path': e_path.get().strip() or self.uploader.repo_path,
                    'url': e_url.get().strip() or self.uploader.repo_url,
                    'branch': e_branch.get().strip() or self.uploader.branch,
                    'interval': int(e_interval.get().strip() or self.uploader.auto_upload_interval or 10),
                    'prefix': e_prefix.get().strip() or self.uploader.auto_upload_prefix or 'Auto update',
                }
                self.uploader.save_profile(name, prof)
                refresh_list()
                messagebox.showinfo('Profile', f'Đã lưu profile "{name}"')
            ttk.Button(btns, text='Lưu thành profile mới', command=on_save_as).pack(side='left', padx=8)

            def on_load():
                sel = lb.curselection()
                if not sel:
                    return
                name = lb.get(sel[0])
                prof = self.uploader.get_profile(name) or {}
                e_path.delete(0, 'end'); e_path.insert(0, prof.get('path',''))
                e_url.delete(0, 'end'); e_url.insert(0, prof.get('url',''))
                e_branch.delete(0, 'end'); e_branch.insert(0, prof.get('branch',''))
                e_interval.delete(0, 'end'); e_interval.insert(0, str(prof.get('interval','')))
                e_prefix.delete(0, 'end'); e_prefix.insert(0, prof.get('prefix',''))
            ttk.Button(btns, text='Tải từ profile đã chọn', command=on_load).pack(side='left', padx=8)

            def on_apply_to_current():
                # Apply to current and save
                self.uploader.repo_path = e_path.get().strip() or self.uploader.repo_path
                self.uploader.repo_url = e_url.get().strip() or self.uploader.repo_url
                self.uploader.branch = e_branch.get().strip() or self.uploader.branch
                try:
                    self.uploader.auto_upload_interval = int(e_interval.get().strip() or self.uploader.auto_upload_interval)
                except Exception:
                    pass
                self.uploader.auto_upload_prefix = e_prefix.get().strip() or self.uploader.auto_upload_prefix
                self.uploader.save_config()
                messagebox.showinfo('Cấu hình', 'Đã áp dụng vào cấu hình hiện tại')
            ttk.Button(btns, text='Áp dụng vào cấu hình hiện tại', command=on_apply_to_current).pack(side='left', padx=8)

            def on_delete():
                sel = lb.curselection()
                if not sel:
                    return
                name = lb.get(sel[0])
                if self.uploader.delete_profile(name):
                    refresh_list()
                    messagebox.showinfo('Profile', f'Đã xoá "{name}"')
            ttk.Button(btns, text='Xoá profile đã chọn', command=on_delete).pack(side='left', padx=8)

            # Seed current config into editors
            e_path.insert(0, self.uploader.repo_path or '')
            e_url.insert(0, self.uploader.repo_url or '')
            e_branch.insert(0, self.uploader.branch or '')
            e_interval.insert(0, str(self.uploader.auto_upload_interval or 10))
            e_prefix.insert(0, self.uploader.auto_upload_prefix or 'Auto update')
            refresh_list()
        except Exception as e:
            messagebox.showerror("Cấu hình", str(e))

    def start_auto_upload(self):
        self.start_background_mode()

    def view_logs(self):
        log_dir = os.path.join(Path.home(), ".github_uploader_logs")
        os.makedirs(log_dir, exist_ok=True)
        try:
            if sys.platform.startswith('win'):
                os.startfile(log_dir)  # type: ignore[attr-defined]
            elif sys.platform == 'darwin':
                subprocess.run(["open", log_dir])
            else:
                subprocess.run(["xdg-open", log_dir])
        except Exception as e:
            messagebox.showerror("Logs", f"Cannot open logs: {e}")

class GitHubUploaderGUI:
    def __init__(self, uploader):
        self.uploader = uploader
        self.root = tk.Tk()
        self.root.title("GitHub Auto Upload Tool Pro")
        self.root.geometry("420x420")
        self.root.resizable(False, False)
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Segoe UI', 11), padding=8)
        self.style.configure('TLabel', font=('Segoe UI', 13))
        # Taskbar/toast notifications (Windows)
        self._toast_available = False
        self._toaster = None
        try:
            from win10toast import ToastNotifier  # type: ignore
            self._toaster = ToastNotifier()
            self._toast_available = True
        except Exception:
            self._toast_available = False
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill='both')

        logo = tk.PhotoImage(width=1, height=1)  # Placeholder image
        ttk.Label(frame, text="GitHub Auto Upload Tool Pro", style='TLabel').pack(pady=(0, 12))

        ttk.Button(frame, text="[UPLOAD] Upload code lên GitHub", image=logo, compound='left', command=self.upload_code).pack(fill='x', pady=6)
        ttk.Button(frame, text="[GIT STATUS] Xem trạng thái Git", image=logo, compound='left', command=self.show_git_status).pack(fill='x', pady=6)
        ttk.Button(frame, text="[EDIT] Tạo/Sửa .gitignore", image=logo, compound='left', command=self.create_gitignore).pack(fill='x', pady=6)
        ttk.Button(frame, text="[CONFIG] Quản lý cấu hình đã lưu", image=logo, compound='left', command=self.manage_saved_configs).pack(fill='x', pady=6)
        ttk.Button(frame, text="[TIME] Cấu hình tự động upload", image=logo, compound='left', command=self.configure_auto_upload).pack(fill='x', pady=6)
        # Background controls
        ttk.Button(frame, text="[BG START] Bật chạy nền (tiến trình tách biệt)", image=logo, compound='left', command=self.start_background_gui).pack(fill='x', pady=6)
        ttk.Button(frame, text="[BG STOP] Dừng chạy nền", image=logo, compound='left', command=self.stop_background_gui).pack(fill='x', pady=6)
        ttk.Button(frame, text="[BG STATUS] Trạng thái nền", image=logo, compound='left', command=self.show_bg_status_window).pack(fill='x', pady=6)
        ttk.Button(frame, text="[LOG] Xem logs", image=logo, compound='left', command=self.view_logs).pack(fill='x', pady=6)
        ttk.Button(frame, text="[EXIT] Thoát", image=logo, compound='left', command=self.root.quit).pack(fill='x', pady=6)

        # Footer
        ttk.Label(frame, text="© 2025 by GitHub Auto Upload Team", font=('Segoe UI', 9)).pack(side='bottom', pady=(18,0))

    def upload_code(self):
        try:
            self.uploader.git_add_all()
            self.uploader.git_commit("Upload từ GUI")
            self.uploader.git_push()
            messagebox.showinfo("Thành công", "Đã upload code lên GitHub!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def show_git_status(self):
        try:
            self.uploader.show_git_status()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def create_gitignore(self):
        try:
            self.uploader.create_gitignore()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def manage_saved_configs(self):
        try:
            self.uploader.manage_saved_configs()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def configure_auto_upload(self):
        try:
            self.uploader.start_auto_upload()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def view_logs(self):
        try:
            self.uploader.view_logs()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
    
    # -------- Background controls (GUI) --------
    def start_background_gui(self):
        try:
            self.uploader.start_background_mode()
        except Exception as e:
            messagebox.showerror("Background", str(e))

    def stop_background_gui(self):
        try:
            ok = self.uploader.stop_background_mode()
            if ok:
                messagebox.showinfo("Background", "Đã gửi yêu cầu dừng")
            else:
                messagebox.showinfo("Background", "Không tìm thấy tiến trình nền")
        except Exception as e:
            messagebox.showerror("Background", str(e))

    def show_bg_status_window(self):
        try:
            win = tk.Toplevel(self.root)
            win.title("Trạng thái chạy nền")
            win.geometry("520x320")
            container = ttk.Frame(win, padding=12)
            container.pack(expand=True, fill='both')
            # Header actions
            actions = ttk.Frame(container)
            actions.pack(fill='x', pady=(0, 8))
            refresh_btn = ttk.Button(actions, text="Refresh")
            refresh_btn.pack(side='left')
            notify_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(actions, text='Notify on change', variable=notify_var).pack(side='left', padx=10)

            # Grid of fields
            grid = ttk.Frame(container)
            grid.pack(expand=True, fill='both')
            labels = {}
            fields = [
                ('PID', 'pid'),
                ('Running', 'running'),
                ('Last time', 'timestamp'),
                ('Result', 'result'),
                ('Message', 'message'),
                ('Repository', 'path'),
                ('Branch', 'branch'),
                ('Interval (m)', 'interval'),
                ('Prefix', 'prefix'),
            ]
            for i, (title, key) in enumerate(fields):
                ttk.Label(grid, text=title+':', width=14).grid(column=0, row=i, sticky='w', pady=2)
                val = ttk.Label(grid, text='')
                val.grid(column=1, row=i, sticky='w', pady=2)
                labels[key] = val

            last_result = {'value': None}

            def push_toast(title: str, msg: str):
                if self._toast_available:
                    try:
                        self._toaster.show_toast(title, msg, duration=4, threaded=True)
                    except Exception:
                        pass

            def do_refresh():
                pid = self.uploader._read_bg_pid()
                running = self.uploader.is_background_running()
                st = self.uploader.read_status() or {}
                # Update labels
                labels['pid'].config(text=str(pid or ''))
                labels['running'].config(text='Yes' if running else 'No')
                labels['timestamp'].config(text=st.get('timestamp', ''))
                labels['result'].config(text=st.get('result', ''))
                labels['message'].config(text=st.get('message', ''))
                labels['path'].config(text=st.get('path', ''))
                labels['branch'].config(text=st.get('branch', ''))
                labels['interval'].config(text=str(st.get('interval', '')))
                labels['prefix'].config(text=st.get('prefix', ''))
                # Notify on result change
                res = st.get('result') if st else None
                if notify_var.get() and res and res != last_result['value']:
                    push_toast('Background status changed', f"{res} at {st.get('timestamp','')}")
                last_result['value'] = res

            def auto_refresh():
                do_refresh()
                win.after(3000, auto_refresh)

            refresh_btn.config(command=do_refresh)
            do_refresh()
            auto_refresh()
        except Exception as e:
            messagebox.showerror("Background", str(e))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    import sys, os, subprocess, logging
    uploader = GitHubUploader()
    if '--run-background' in sys.argv:
        # Detached background entrypoint
        uploader.run_background_loop()
    else:
        gui = GitHubUploaderGUI(uploader)
        gui.run()

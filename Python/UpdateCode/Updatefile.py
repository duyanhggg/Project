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
            win = tk.Toplevel()
            win.title("Quản lý cấu hình")
            win.geometry("700x450")
            win.configure(bg='#1e1e1e')
            
            # Main container with modern styling
            main_frame = tk.Frame(win, bg='#1e1e1e')
            main_frame.pack(expand=True, fill='both', padx=20, pady=20)

            # Title
            title_label = tk.Label(main_frame, text="⚙️ Quản Lý Profiles", 
                                   font=('Segoe UI', 16, 'bold'), 
                                   bg='#1e1e1e', fg='#ffffff')
            title_label.pack(pady=(0, 20))

            # Content frame
            content_frame = tk.Frame(main_frame, bg='#1e1e1e')
            content_frame.pack(expand=True, fill='both')

            # Left panel - Profiles list
            left_panel = tk.Frame(content_frame, bg='#2d2d2d', relief='flat', bd=0)
            left_panel.pack(side='left', fill='both', padx=(0, 15), pady=0)
            left_panel.config(width=200)

            tk.Label(left_panel, text='📋 Profiles', font=('Segoe UI', 11, 'bold'),
                    bg='#2d2d2d', fg='#ffffff').pack(anchor='w', padx=10, pady=(10, 5))
            
            lb = tk.Listbox(left_panel, height=15, bg='#2d2d2d', fg='#ffffff',
                           selectbackground='#0078d4', selectforeground='#ffffff',
                           font=('Segoe UI', 10), relief='flat', bd=0,
                           highlightthickness=1, highlightbackground='#3d3d3d')
            lb.pack(padx=10, pady=(0, 10), fill='both', expand=True)

            def refresh_list():
                lb.delete(0, 'end')
                for name in self.list_profiles():
                    lb.insert('end', f"  {name}")

            # Right panel - Edit form
            right_panel = tk.Frame(content_frame, bg='#2d2d2d', relief='flat', bd=0)
            right_panel.pack(side='left', fill='both', expand=True)

            # Form fields with modern style
            form_frame = tk.Frame(right_panel, bg='#2d2d2d')
            form_frame.pack(padx=15, pady=15, fill='both', expand=True)

            entries = {}
            fields = [
                ('📁 Path', 'path', 40),
                ('🔗 URL', 'url', 40),
                ('🌿 Branch', 'branch', 20),
                ('⏱️ Interval (min)', 'interval', 10),
                ('✏️ Prefix', 'prefix', 30),
            ]

            for i, (label, key, width) in enumerate(fields):
                field_frame = tk.Frame(form_frame, bg='#2d2d2d')
                field_frame.pack(fill='x', pady=8)
                
                tk.Label(field_frame, text=label, font=('Segoe UI', 10),
                        bg='#2d2d2d', fg='#cccccc', width=18, anchor='w').pack(side='left')
                
                entry = tk.Entry(field_frame, width=width, bg='#3d3d3d', fg='#ffffff',
                               font=('Segoe UI', 10), relief='flat', bd=0,
                               insertbackground='#ffffff')
                entry.pack(side='left', padx=5, ipady=5)
                entries[key] = entry

            # Buttons with modern styling
            button_frame = tk.Frame(right_panel, bg='#2d2d2d')
            button_frame.pack(padx=15, pady=(0, 15), fill='x')

            def create_modern_button(parent, text, command, bg_color='#0078d4'):
                btn = tk.Button(parent, text=text, command=command,
                              bg=bg_color, fg='#ffffff',
                              font=('Segoe UI', 9, 'bold'),
                              relief='flat', bd=0, padx=12, pady=6,
                              cursor='hand2', activebackground='#005a9e',
                              activeforeground='#ffffff')
                return btn

            btn_row1 = tk.Frame(button_frame, bg='#2d2d2d')
            btn_row1.pack(fill='x', pady=3)
            
            def choose_path():
                p = filedialog.askdirectory(title='Chọn thư mục repository', 
                                           initialdir=entries['path'].get() or self.repo_path)
                if p:
                    entries['path'].delete(0, 'end')
                    entries['path'].insert(0, p)
            
            create_modern_button(btn_row1, '📂 Chọn thư mục', choose_path, '#2d7d2d').pack(side='left', padx=2)

            def on_save_as():
                name = simpledialog.askstring('Lưu cấu hình', 'Tên profile:')
                if not name:
                    return
                prof = {
                    'path': entries['path'].get().strip() or self.repo_path,
                    'url': entries['url'].get().strip() or self.repo_url,
                    'branch': entries['branch'].get().strip() or self.branch,
                    'interval': int(entries['interval'].get().strip() or self.auto_upload_interval or 10),
                    'prefix': entries['prefix'].get().strip() or self.auto_upload_prefix or 'Auto update',
                }
                self.save_profile(name, prof)
                refresh_list()
                messagebox.showinfo('✅ Success', f'Đã lưu profile "{name}"')
            
            create_modern_button(btn_row1, '💾 Lưu Profile', on_save_as, '#0078d4').pack(side='left', padx=2)

            btn_row2 = tk.Frame(button_frame, bg='#2d2d2d')
            btn_row2.pack(fill='x', pady=3)

            def on_load():
                sel = lb.curselection()
                if not sel:
                    return
                name = lb.get(sel[0]).strip()
                prof = self.get_profile(name) or {}
                entries['path'].delete(0, 'end')
                entries['path'].insert(0, prof.get('path',''))
                entries['url'].delete(0, 'end')
                entries['url'].insert(0, prof.get('url',''))
                entries['branch'].delete(0, 'end')
                entries['branch'].insert(0, prof.get('branch',''))
                entries['interval'].delete(0, 'end')
                entries['interval'].insert(0, str(prof.get('interval','')))
                entries['prefix'].delete(0, 'end')
                entries['prefix'].insert(0, prof.get('prefix',''))
            
            create_modern_button(btn_row2, '📥 Tải Profile', on_load, '#6d4c9d').pack(side='left', padx=2)

            def on_apply():
                self.repo_path = entries['path'].get().strip() or self.repo_path
                self.repo_url = entries['url'].get().strip() or self.repo_url
                self.branch = entries['branch'].get().strip() or self.branch
                try:
                    self.auto_upload_interval = int(entries['interval'].get().strip() or self.auto_upload_interval)
                except Exception:
                    pass
                self.auto_upload_prefix = entries['prefix'].get().strip() or self.auto_upload_prefix
                self.save_config()
                messagebox.showinfo('✅ Success', 'Đã áp dụng cấu hình!')
            
            create_modern_button(btn_row2, '✅ Áp dụng', on_apply, '#2d7d2d').pack(side='left', padx=2)

            def on_delete():
                sel = lb.curselection()
                if not sel:
                    return
                name = lb.get(sel[0]).strip()
                if messagebox.askyesno('Xác nhận', f'Xóa profile "{name}"?'):
                    if self.delete_profile(name):
                        refresh_list()
                        messagebox.showinfo('✅ Success', f'Đã xóa "{name}"')
            
            create_modern_button(btn_row2, '🗑️ Xóa', on_delete, '#d42d2d').pack(side='left', padx=2)

            # Load current config
            entries['path'].insert(0, self.repo_path or '')
            entries['url'].insert(0, self.repo_url or '')
            entries['branch'].insert(0, self.branch or '')
            entries['interval'].insert(0, str(self.auto_upload_interval or 10))
            entries['prefix'].insert(0, self.auto_upload_prefix or 'Auto update')
            refresh_list()
            
        except Exception as e:
            messagebox.showerror("❌ Lỗi", str(e))
    
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
        self.root.geometry("600x750")
        self.root.resizable(False, False)
        
        # Modern dark theme colors
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#0078d4',
            'success': '#2d7d2d',
            'warning': '#d49d2d',
            'danger': '#d42d2d',
            'card': '#2d2d2d',
            'border': '#3d3d3d',
            'text_secondary': '#cccccc'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
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

    def create_modern_button(self, parent, text, command, icon='', color_key='accent'):
        """Create a modern styled button"""
        btn_frame = tk.Frame(parent, bg=self.colors['card'], highlightthickness=1, 
                            highlightbackground=self.colors['border'])
        btn_frame.pack(fill='x', pady=5, padx=10)
        
        btn = tk.Button(btn_frame, text=f"{icon} {text}", command=command,
                       bg=self.colors['card'], fg=self.colors['fg'],
                       font=('Segoe UI', 11), relief='flat', bd=0,
                       anchor='w', padx=20, pady=12, cursor='hand2')
        btn.pack(fill='both', expand=True)
        
        # Hover effects
        def on_enter(e):
            btn.config(bg=self.colors[color_key])
        
        def on_leave(e):
            btn.config(bg=self.colors['card'])
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn

    def create_widgets(self):
        # Header with gradient effect
        header = tk.Frame(self.root, bg=self.colors['accent'], height=100)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="⚡", font=('Segoe UI', 32), 
                bg=self.colors['accent'], fg=self.colors['fg']).pack(pady=(15, 0))
        tk.Label(header, text="GitHub Auto Upload Pro", 
                font=('Segoe UI', 18, 'bold'), 
                bg=self.colors['accent'], fg=self.colors['fg']).pack()
        tk.Label(header, text="Tự động hóa việc đẩy code lên GitHub", 
                font=('Segoe UI', 9), 
                bg=self.colors['accent'], fg='#e0e0e0').pack(pady=(2, 0))

        # Main content area
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Info card
        info_card = tk.Frame(main_frame, bg=self.colors['card'], 
                            highlightthickness=1, highlightbackground=self.colors['border'])
        info_card.pack(fill='x', pady=(0, 15))
        
        info_content = tk.Frame(info_card, bg=self.colors['card'])
        info_content.pack(padx=15, pady=12)
        
        repo_text = self.uploader.repo_path if self.uploader.repo_path else "Chưa cấu hình"
        tk.Label(info_content, text=f"📁 Repository: {repo_text}", 
                font=('Segoe UI', 9), bg=self.colors['card'], 
                fg=self.colors['text_secondary'], anchor='w').pack(fill='x')
        
        branch_text = self.uploader.branch if self.uploader.branch else "main"
        tk.Label(info_content, text=f"🌿 Branch: {branch_text}", 
                font=('Segoe UI', 9), bg=self.colors['card'], 
                fg=self.colors['text_secondary'], anchor='w').pack(fill='x')

        # Section: Git Operations
        section1 = tk.LabelFrame(main_frame, text=" 🔧 Git Operations ", 
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.colors['bg'], fg=self.colors['fg'],
                                relief='flat', bd=0)
        section1.pack(fill='x', pady=(0, 10))

        self.create_modern_button(section1, "Upload Code", self.upload_code, '🚀', 'success')
        self.create_modern_button(section1, "Git Status", self.show_git_status, '📊', 'accent')
        self.create_modern_button(section1, "Tạo/Sửa .gitignore", self.create_gitignore, '📝', 'accent')

        # Section: Configuration
        section2 = tk.LabelFrame(main_frame, text=" ⚙️ Configuration ", 
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.colors['bg'], fg=self.colors['fg'],
                                relief='flat', bd=0)
        section2.pack(fill='x', pady=(0, 10))

        self.create_modern_button(section2, "Quản lý Profiles", self.manage_saved_configs, '💾', 'accent')
        self.create_modern_button(section2, "Cấu hình Auto Upload", self.configure_auto_upload, '⏰', 'warning')

        # Section: Background Mode
        section3 = tk.LabelFrame(main_frame, text=" 🔄 Background Mode ", 
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.colors['bg'], fg=self.colors['fg'],
                                relief='flat', bd=0)
        section3.pack(fill='x', pady=(0, 10))

        self.create_modern_button(section3, "Bật chạy nền", self.start_background_gui, '▶️', 'success')
        self.create_modern_button(section3, "Dừng chạy nền", self.stop_background_gui, '⏸️', 'danger')
        self.create_modern_button(section3, "Trạng thái nền", self.show_bg_status_window, '📡', 'accent')

        # Section: Utilities
        section4 = tk.LabelFrame(main_frame, text=" 🛠️ Utilities ", 
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.colors['bg'], fg=self.colors['fg'],
                                relief='flat', bd=0)
        section4.pack(fill='x', pady=(0, 10))

        self.create_modern_button(section4, "Xem Logs", self.view_logs, '📄', 'accent')
        self.create_modern_button(section4, "Thoát", self.root.quit, '🚪', 'danger')

        # Footer
        footer = tk.Frame(self.root, bg=self.colors['bg'])
        footer.pack(side='bottom', fill='x', pady=(0, 10))
        
        tk.Label(footer, text="© 2025 GitHub Auto Upload Team • Made with ❤️", 
                font=('Segoe UI', 8), bg=self.colors['bg'], 
                fg=self.colors['text_secondary']).pack()

    def upload_code(self):
        try:
            # Show progress window
            progress_win = tk.Toplevel(self.root)
            progress_win.title("Uploading...")
            progress_win.geometry("400x150")
            progress_win.configure(bg=self.colors['bg'])
            progress_win.transient(self.root)
            progress_win.grab_set()
            
            tk.Label(progress_win, text="⏳ Đang upload code...", 
                    font=('Segoe UI', 12, 'bold'),
                    bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=20)
            
            status_label = tk.Label(progress_win, text="Đang thực hiện git add...",
                                   font=('Segoe UI', 10),
                                   bg=self.colors['bg'], fg=self.colors['text_secondary'])
            status_label.pack()
            
            def do_upload():
                try:
                    status_label.config(text="📦 Git add...")
                    self.uploader.git_add_all()
                    
                    status_label.config(text="💬 Git commit...")
                    self.uploader.git_commit("Upload từ GUI")
                    
                    status_label.config(text="🚀 Git push...")
                    self.uploader.git_push()
                    
                    progress_win.destroy()
                    messagebox.showinfo("✅ Thành công", "Đã upload code lên GitHub!")
                except Exception as e:
                    progress_win.destroy()
                    messagebox.showerror("❌ Lỗi", str(e))
            
            self.root.after(100, do_upload)
            
        except Exception as e:
            messagebox.showerror("❌ Lỗi", str(e))
    
    def show_git_status(self):
        try:
            self.uploader.show_git_status()
        except Exception as e:
            messagebox.showerror("❌ Lỗi", str(e))

    def create_gitignore(self):
        try:
            self.uploader.create_gitignore()
        except Exception as e:
            messagebox.showerror("❌ Lỗi", str(e))
    
    def manage_saved_configs(self):
        try:
            self.uploader.manage_saved_configs()
        except Exception as e:
            messagebox.showerror("❌ Lỗi", str(e))

    def configure_auto_upload(self):
        try:
            self.uploader.start_auto_upload()
        except Exception as e:
            messagebox.showerror("❌ Lỗi", str(e))

    def view_logs(self):
        try:
            self.uploader.view_logs()
        except Exception as e:
            messagebox.showerror("❌ Lỗi", str(e))
    
    # -------- Background controls (GUI) --------
    def start_background_gui(self):
        try:
            self.uploader.start_background_mode()
        except Exception as e:
            messagebox.showerror("❌ Background", str(e))

    def stop_background_gui(self):
        try:
            ok = self.uploader.stop_background_mode()
            if ok:
                messagebox.showinfo("✅ Background", "Đã gửi yêu cầu dừng")
            else:
                messagebox.showinfo("ℹ️ Background", "Không tìm thấy tiến trình nền")
        except Exception as e:
            messagebox.showerror("❌ Background", str(e))

    def show_bg_status_window(self):
        try:
            win = tk.Toplevel(self.root)
            win.title("Trạng thái chạy nền")
            win.geometry("650x450")
            win.configure(bg=self.colors['bg'])
            
            # Header
            header = tk.Frame(win, bg=self.colors['accent'], height=60)
            header.pack(fill='x')
            header.pack_propagate(False)
            
            tk.Label(header, text="📡 Trạng thái Background Service", 
                    font=('Segoe UI', 14, 'bold'),
                    bg=self.colors['accent'], fg=self.colors['fg']).pack(pady=15)
            
            # Main container
            container = tk.Frame(win, bg=self.colors['bg'])
            container.pack(expand=True, fill='both', padx=20, pady=20)
            
            # Actions bar
            actions = tk.Frame(container, bg=self.colors['card'],
                             highlightthickness=1, highlightbackground=self.colors['border'])
            actions.pack(fill='x', pady=(0, 15))
            
            actions_inner = tk.Frame(actions, bg=self.colors['card'])
            actions_inner.pack(padx=10, pady=10, fill='x')
            
            refresh_btn = tk.Button(actions_inner, text="🔄 Refresh", 
                                   bg=self.colors['accent'], fg=self.colors['fg'],
                                   font=('Segoe UI', 9, 'bold'), relief='flat',
                                   padx=15, pady=5, cursor='hand2')
            refresh_btn.pack(side='left')
            
            notify_var = tk.BooleanVar(value=True)
            tk.Checkbutton(actions_inner, text='🔔 Thông báo khi có thay đổi', 
                          variable=notify_var, bg=self.colors['card'],
                          fg=self.colors['text_secondary'], font=('Segoe UI', 9),
                          selectcolor=self.colors['bg'], activebackground=self.colors['card'],
                          activeforeground=self.colors['fg']).pack(side='left', padx=15)

            # Status grid
            grid_frame = tk.Frame(container, bg=self.colors['card'],
                                 highlightthickness=1, highlightbackground=self.colors['border'])
            grid_frame.pack(expand=True, fill='both')
            
            grid_inner = tk.Frame(grid_frame, bg=self.colors['card'])
            grid_inner.pack(padx=20, pady=20, fill='both', expand=True)
            
            labels = {}
            fields = [
                ('🆔 PID', 'pid'),
                ('▶️ Running', 'running'),
                ('🕐 Last Update', 'timestamp'),
                ('📊 Result', 'result'),
                ('💬 Message', 'message'),
                ('📁 Repository', 'path'),
                ('🌿 Branch', 'branch'),
                ('⏱️ Interval (min)', 'interval'),
                ('✏️ Prefix', 'prefix'),
            ]
            
            for i, (title, key) in enumerate(fields):
                row_frame = tk.Frame(grid_inner, bg=self.colors['card'])
                row_frame.pack(fill='x', pady=5)
                
                tk.Label(row_frame, text=title, font=('Segoe UI', 10),
                        bg=self.colors['card'], fg=self.colors['text_secondary'],
                        width=20, anchor='w').pack(side='left')
                
                val = tk.Label(row_frame, text='', font=('Segoe UI', 10, 'bold'),
                              bg=self.colors['card'], fg=self.colors['fg'],
                              anchor='w')
                val.pack(side='left', fill='x', expand=True)
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
                
                # Update labels with colors
                labels['pid'].config(text=str(pid or 'N/A'))
                
                if running:
                    labels['running'].config(text='✅ Yes', fg='#2d7d2d')
                else:
                    labels['running'].config(text='❌ No', fg='#d42d2d')
                
                labels['timestamp'].config(text=st.get('timestamp', 'N/A'))
                
                result = st.get('result', 'N/A')
                if result == 'success':
                    labels['result'].config(text=f'✅ {result}', fg='#2d7d2d')
                elif result == 'failure':
                    labels['result'].config(text=f'❌ {result}', fg='#d42d2d')
                else:
                    labels['result'].config(text=f'ℹ️ {result}', fg='#d49d2d')
                
                labels['message'].config(text=st.get('message', 'N/A'))
                labels['path'].config(text=st.get('path', 'N/A'))
                labels['branch'].config(text=st.get('branch', 'N/A'))
                labels['interval'].config(text=str(st.get('interval', 'N/A')))
                labels['prefix'].config(text=st.get('prefix', 'N/A'))
                
                # Notify on result change
                res = st.get('result') if st else None
                if notify_var.get() and res and res != last_result['value']:
                    push_toast('🔔 Background status changed', 
                             f"{res} at {st.get('timestamp','')}")
                last_result['value'] = res

            def auto_refresh():
                do_refresh()
                win.after(3000, auto_refresh)

            refresh_btn.config(command=do_refresh)
            do_refresh()
            auto_refresh()
            
        except Exception as e:
            messagebox.showerror("❌ Background", str(e))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    uploader = GitHubUploader()
    if '--run-background' in sys.argv:
        # Detached background entrypoint
        uploader.run_background_loop()
    else:
        gui = GitHubUploaderGUI(uploader)
        gui.run()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Auto Upload Tool Pro
Công cụ tự động đẩy code lên GitHub với nhiều tính năng nâng cao
Version 2.4 - Enhanced UI with Modern Design
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
import pystray
from PIL import Image, ImageDraw


class GitHubUploader:
    def __init__(self):
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
                # UI Settings
                self.theme = data.get("theme", "github_dark")
                self.language = data.get("language", "vi")
                self.enable_tray = data.get("enable_tray", True)
                self.auto_start = data.get("auto_start", False)
                self.auto_update_notify = data.get("auto_update_notify", True)
        except Exception:
            pass
        finally:
            # Set defaults if not loaded
            if not hasattr(self, 'theme'):
                self.theme = "github_dark"
            if not hasattr(self, 'language'):
                self.language = "vi"
            if not hasattr(self, 'enable_tray'):
                self.enable_tray = True
            if not hasattr(self, 'auto_start'):
                self.auto_start = False
            if not hasattr(self, 'auto_update_notify'):
                self.auto_update_notify = True

    def save_config(self):
        try:
            data = {
                "path": self.repo_path,
                "url": self.repo_url,
                "branch": self.branch,
                "interval": self.auto_upload_interval,
                "prefix": self.auto_upload_prefix,
                "profiles": getattr(self, "_profiles", {}),
                "theme": getattr(self, 'theme', 'github_dark'),
                "language": getattr(self, 'language', 'vi'),
                "enable_tray": getattr(self, 'enable_tray', True),
                "auto_start": getattr(self, 'auto_start', False),
                "auto_update_notify": getattr(self, 'auto_update_notify', True),
            }
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

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
        if not ok and ("nothing to commit" in (out + err).lower()):
            return True
        return ok

    def git_push(self) -> bool:
        self.init_git_repo()
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

    def start_background_mode(self) -> bool:
        if self.is_background_running():
            messagebox.showinfo("Background", "Đã chạy nền")
            return True
        if not self.configure_remote():
            return False
        self.save_config()
        try:
            cmd = f'"{sys.executable}" "{os.path.abspath(__file__)}" --run-background'
            creationflags = 0
            if sys.platform.startswith('win'):
                creationflags = 0x08000000
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL, creationflags=creationflags)
            with open(self.bg_pid_file, 'w', encoding='utf-8') as f:
                f.write(str(proc.pid))
            messagebox.showinfo("Background", "Đã bật chạy nền")
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
                subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                os.kill(pid, 15)
            return True
        except Exception:
            return False

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
                out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], 
                                   capture_output=True, text=True)
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

    def run_background_loop(self):
        try:
            with open(self.bg_pid_file, 'w', encoding='utf-8') as f:
                f.write(str(os.getpid()))
        except Exception:
            pass
        self._write_status('start', 'Background loop started')
        while True:
            try:
                self.load_config()
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
            interval_sec = max(60, int(self.auto_upload_interval) * 60)
            time.sleep(interval_sec)

    def view_logs(self):
        log_dir = os.path.join(Path.home(), ".github_uploader_logs")
        os.makedirs(log_dir, exist_ok=True)
        try:
            if sys.platform.startswith('win'):
                os.startfile(log_dir)
            elif sys.platform == 'darwin':
                subprocess.run(["open", log_dir])
            else:
                subprocess.run(["xdg-open", log_dir])
        except Exception as e:
            messagebox.showerror("Logs", f"Cannot open logs: {e}")


class SystemTrayManager:
    """Quản lý System Tray"""
    
    def __init__(self, gui_app):
        self.gui_app = gui_app
        self.icon = None
        
    def create_image(self):
        """Tạo icon cho system tray"""
        width = 64
        height = 64
        color_bg = (138, 43, 226)  # Blue Violet
        color_fg = (255, 215, 0)  # Gold
        
        image = Image.new('RGB', (width, height), color_bg)
        dc = ImageDraw.Draw(image)
        
        # Draw GitHub logo style
        # Circle
        dc.ellipse([8, 8, 56, 56], fill=color_fg)
        # Inner circle
        dc.ellipse([20, 20, 44, 44], fill=color_bg)
        # Arrow up
        dc.polygon([(32, 16), (26, 22), (30, 22), (30, 38), (34, 38), (34, 22), (38, 22)], 
                  fill=color_fg)
        
        return image
    
    def show_window(self, icon=None, item=None):
        """Hiển thị cửa sổ"""
        self.gui_app.root.after(0, self.gui_app.root.deiconify)
        self.gui_app.root.after(0, self.gui_app.root.lift)
        self.gui_app.root.after(0, self.gui_app.root.focus_force)
    
    def hide_window(self):
        """Ẩn cửa sổ"""
        self.gui_app.root.withdraw()
    
    def upload_now(self, icon=None, item=None):
        """Upload ngay từ tray"""
        try:
            self.gui_app.uploader.git_add_all()
            self.gui_app.uploader.git_commit(f"Quick upload {datetime.now().strftime('%H:%M')}")
            self.gui_app.uploader.git_push()
            if self.icon:
                try:
                    self.icon.notify("✅ Upload thành công", "GitHub Auto Upload")
                except:
                    pass
        except Exception as e:
            if self.icon:
                try:
                    self.icon.notify(f"❌ Lỗi: {str(e)}", "GitHub Auto Upload")
                except:
                    pass
    
    def show_status(self, icon=None, item=None):
        """Hiển thị status"""
        running = self.gui_app.uploader.is_background_running()
        status = "🟢 Đang chạy" if running else "🔴 Đã dừng"
        
        try:
            self.icon.notify(f"Background: {status}", "GitHub Auto Upload")
        except:
            pass
    
    def quit_app(self, icon=None, item=None):
        """Thoát ứng dụng"""
        if self.icon:
            self.icon.stop()
        self.gui_app.root.quit()
    
    def setup_tray(self):
        """Thiết lập system tray"""
        menu = pystray.Menu(
            pystray.MenuItem('🚀 GitHub Auto Upload Pro', self.show_window, default=True),
            pystray.MenuItem('━━━━━━━━━━━━━━━━━━', lambda: None, enabled=False),
            pystray.MenuItem('📂 Show Window', self.show_window),
            pystray.MenuItem('⚡ Upload Now', self.upload_now),
            pystray.MenuItem('📊 Background Status', self.show_status),
            pystray.MenuItem('━━━━━━━━━━━━━━━━━━', lambda: None, enabled=False),
            pystray.MenuItem('❌ Exit', self.quit_app)
        )
        
        self.icon = pystray.Icon('github_uploader', self.create_image(), 
                                'GitHub Auto Upload Pro', menu)
    
    def run(self):
        """Chạy system tray"""
        self.icon.run()


class GitHubUploaderGUI:
    def __init__(self, uploader):
        self.uploader = uploader
        self.root = tk.Tk()
        self.root.title("GitHub Auto Upload Tool Pro")
        self.root.geometry("700x700")
        self.root.minsize(500, 600)
        
        # Load UI settings
        self.load_ui_settings()
        
        # System tray manager
        self.tray_manager = SystemTrayManager(self)
        
        self.create_widgets()
        self.center_window()
        self.setup_window_events()
        
        # Start system tray if enabled
        if getattr(self.uploader, 'enable_tray', True):
            self.start_system_tray()
    
    def load_ui_settings(self):
        """Load theme and language settings"""
        self.themes = {
            'github_dark': {
                'bg': '#0d1117', 'card': '#161b22', 'card_hover': '#1c2128',
                'fg': '#c9d1d9', 'fg_secondary': '#8b949e', 'accent': '#6f42c1',
                'accent_light': '#a371f7', 'success': '#3fb950', 'warning': '#d29922',
                'danger': '#f85149', 'border': '#30363d'
            },
            'blue_dark': {
                'bg': '#1a1f35', 'card': '#252b42', 'card_hover': '#2d3450',
                'fg': '#e0e5ff', 'fg_secondary': '#a8b0d9', 'accent': '#5b7cff',
                'accent_light': '#8fa3ff', 'success': '#4ecdc4', 'warning': '#ffe66d',
                'danger': '#ff6b6b', 'border': '#3a4258'
            },
            'purple_dark': {
                'bg': '#1e1b3a', 'card': '#2a264a', 'card_hover': '#34305a',
                'fg': '#e8e4ff', 'fg_secondary': '#b8a8d9', 'accent': '#9d4edd',
                'accent_light': '#c77dff', 'success': '#06ffa5', 'warning': '#ffbe0b',
                'danger': '#ff006e', 'border': '#40395a'
            },
            'light_white': {
                'bg': '#f5f7fa', 'card': '#ffffff', 'card_hover': '#f0f4f8',
                'fg': '#2d3748', 'fg_secondary': '#718096', 'accent': '#667eea',
                'accent_light': '#764ba2', 'success': '#48bb78', 'warning': '#ed8936',
                'danger': '#f56565', 'border': '#e2e8f0'
            }
        }
        
        current_theme = getattr(self.uploader, 'theme', 'github_dark')
        self.colors = self.themes.get(current_theme, self.themes['github_dark'])
        
        # Load translations
        self.translations = {
            'vi': {
                'title': 'GitHub Auto Upload Pro',
                'subtitle': '✨ Tự động hóa việc đẩy code lên GitHub ✨',
                'tray_tip': '💡 Tip: Minimize to system tray instead of closing',
                'sections': {
                    'quick': '🔧 Thao tác nhanh',
                    'config': '⚙️ Cấu hình',
                    'background': '🔄 Chạy nền',
                    'utils': '🛠️ Tiện ích',
                    'settings': '🎨 Cài đặt'
                },
                'buttons': {
                    'upload': 'Tải lên ngay',
                    'status': 'Trạng thái Git',
                    'gitignore': 'Tạo/Sửa .gitignore',
                    'profiles': 'Quản lý Profile',
                    'auto_settings': 'Cài đặt tự động',
                    'start_bg': 'Bắt đầu chạy nền',
                    'stop_bg': 'Dừng chạy nền',
                    'bg_status': 'Trạng thái chạy nền',
                    'logs': 'Xem nhật ký',
                    'exit': 'Thoát ứng dụng',
                    'settings': 'Cài đặt'
                },
                'settings': {
                    'theme': 'Chủ đề',
                    'language': 'Ngôn ngữ',
                    'tray': 'System Tray',
                    'enable_tray': 'Bật system tray',
                    'auto_start': 'Khởi động cùng Windows',
                    'auto_update_notify': 'Hiển thị thông báo khi tự động cập nhật',
                    'save': 'Lưu & Khởi động lại'
                }
            },
            'en': {
                'title': 'GitHub Auto Upload Pro',
                'subtitle': '✨ Automate GitHub code pushing ✨',
                'tray_tip': '💡 Tip: Minimize to system tray instead of closing',
                'sections': {
                    'quick': '🔧 Quick Actions',
                    'config': '⚙️ Configuration',
                    'background': '🔄 Background Mode',
                    'utils': '🛠️ Utilities',
                    'settings': '🎨 Settings'
                },
                'buttons': {
                    'upload': 'Upload Code Now',
                    'status': 'Git Status',
                    'gitignore': 'Create/Edit .gitignore',
                    'profiles': 'Manage Profiles',
                    'auto_settings': 'Auto Upload Settings',
                    'start_bg': 'Start Background',
                    'stop_bg': 'Stop Background',
                    'bg_status': 'Background Status',
                    'logs': 'View Logs',
                    'exit': 'Exit Application',
                    'settings': 'Settings'
                },
                'settings': {
                    'theme': 'Theme',
                    'language': 'Language',
                    'tray': 'System Tray',
                    'enable_tray': 'Enable system tray',
                    'auto_start': 'Start with Windows',
                    'auto_update_notify': 'Show notifications for auto updates',
                    'save': 'Save & Restart'
                }
            }
        }
        
        self.lang = self.translations.get(getattr(self.uploader, 'language', 'vi'), self.translations['vi'])
        
        self.root.configure(bg=self.colors['bg'])

    def setup_window_events(self):
        """Thiết lập event handlers"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        """Xử lý khi đóng cửa sổ"""
        if getattr(self.uploader, 'enable_tray', True):
            if messagebox.askyesno("Minimize to Tray", 
                                  "Minimize to system tray?\n\n" +
                                  "Click 'No' to exit completely."):
                self.tray_manager.hide_window()
            else:
                self.quit_application()
        else:
            self.quit_application()
    
    def quit_application(self):
        """Thoát ứng dụng"""
        if self.tray_manager.icon:
            self.tray_manager.icon.stop()
        self.root.quit()
    
    def start_system_tray(self):
        """Khởi động system tray"""
        if getattr(self.uploader, 'enable_tray', True):
            self.tray_manager.setup_tray()
            tray_thread = threading.Thread(target=self.tray_manager.run, daemon=True)
            tray_thread.start()

    def center_window(self):
        """Căn giữa cửa sổ"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_modern_button(self, parent, text, command, icon='', color_key='accent'):
        """Create a modern styled button with gradient effect"""
        btn_frame = tk.Frame(parent, bg=self.colors['bg'])
        btn_frame.pack(fill='x', pady=5, padx=15)
        
        # Create a container with rounded shadow effect
        container = tk.Frame(btn_frame, bg=self.colors['card'],
                            relief='flat', bd=0)
        container.pack(fill='x')
        
        btn = tk.Button(container, text=f"{icon}  {text}", command=command,
                       bg=self.colors['card'], fg=self.colors['fg'],
                       font=('Segoe UI', 10, 'bold'), relief='flat', bd=0,
                       anchor='w', padx=25, pady=13, cursor='hand2',
                       activebackground=self.colors['card_hover'],
                       activeforeground=self.colors['accent_light'])
        btn.pack(fill='both', expand=True)
        
        # Enhanced hover effect
        def on_enter(e):
            btn.config(bg=self.colors['card_hover'], 
                      fg=self.colors['accent_light'])
            container.config(bg=self.colors['accent_light'])
            # Add subtle animation effect
            btn.config(padx=27)
        
        def on_leave(e):
            btn.config(bg=self.colors['card'], fg=self.colors['fg'])
            container.config(bg=self.colors['card'])
            btn.config(padx=25)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn

    def create_widgets(self):
        # Enhanced gradient header
        header = tk.Frame(self.root, bg=self.colors['accent'], height=110)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Header content container
        header_content = tk.Frame(header, bg=self.colors['accent'])
        header_content.pack(fill='both', expand=True)
        
        # Icon with enhanced effect
        icon_frame = tk.Frame(header_content, bg=self.colors['accent'])
        icon_frame.pack(pady=(18, 5))
        
        # Animated icon effect
        icon_label = tk.Label(icon_frame, text="🚀", 
                             font=('Segoe UI', 36), 
                             bg=self.colors['accent'], fg='white')
        icon_label.pack()
        
        # Add subtle animation
        def pulse_icon():
            try:
                icon_label.config(fg=self.colors['accent_light'])
                root.after(500, lambda: icon_label.config(fg='white'))
            except:
                pass
        try:
            root = self.root
            root.after(3000, pulse_icon)
        except:
            pass
        
        tk.Label(header_content, text=self.lang['title'], 
                font=('Segoe UI', 20, 'bold'), 
                bg=self.colors['accent'], fg='white').pack(pady=(2, 0))
        tk.Label(header_content, text=self.lang['subtitle'], 
                font=('Segoe UI', 9, 'italic'), 
                bg=self.colors['accent'], fg=self.colors['accent_light']).pack(pady=3)

        # Enhanced tray hint with better styling
        tray_hint = tk.Frame(self.root, bg=self.colors['accent'])
        tray_hint.pack(fill='x')
        tk.Label(tray_hint, text=self.lang['tray_tip'], 
                font=('Segoe UI', 8, 'italic'),
                bg=self.colors['accent'], fg='white').pack(pady=8)

        # Main content với scrollable area
        canvas_container = tk.Frame(self.root, bg=self.colors['bg'])
        canvas_container.pack(expand=True, fill='both', side='top')
        
        canvas = tk.Canvas(canvas_container, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=15)
        scrollbar.pack(side="right", fill="y", pady=15, padx=(0, 15))
        
        main_frame = scrollable_frame

        # Chia 2 cột
        columns = tk.Frame(main_frame, bg=self.colors['bg'])
        columns.pack(fill='both', expand=True)

        left_col = tk.Frame(columns, bg=self.colors['bg'])
        left_col.pack(side='left', fill='both', expand=True, padx=(0, 10))

        right_col = tk.Frame(columns, bg=self.colors['bg'])
        right_col.pack(side='left', fill='y', padx=(10, 0))

        # Info card
        info_card = tk.Frame(left_col, bg=self.colors['card'], 
                            highlightthickness=1, 
                            highlightbackground=self.colors['border'])
        info_card.pack(fill='x', pady=(15, 15), padx=0)

        info_content = tk.Frame(info_card, bg=self.colors['card'])
        info_content.pack(padx=25, pady=15)

        repo_text = self.uploader.repo_path if self.uploader.repo_path else "Chưa cấu hình"
        tk.Label(info_content, text=f"📁  {repo_text[:50]}...", 
                font=('Segoe UI', 10, 'bold'), bg=self.colors['card'], 
                fg=self.colors['fg'], anchor='w').pack(fill='x', pady=3)

        branch_text = self.uploader.branch if self.uploader.branch else "main"
        tk.Label(info_content, text=f"🌿  {branch_text}", 
                font=('Segoe UI', 10), bg=self.colors['card'], 
                fg=self.colors['fg_secondary'], anchor='w').pack(fill='x', pady=2)

        bg_running = self.uploader.is_background_running()
        bg_status_text = "🟢 Running" if bg_running else "🔴 Stopped"
        bg_color = self.colors['success'] if bg_running else self.colors['danger']
        tk.Label(info_content, text=f"⚡  {bg_status_text}", 
                font=('Segoe UI', 10, 'bold'), bg=self.colors['card'], 
                fg=bg_color, anchor='w').pack(fill='x', pady=3)

        # Section: Quick Actions (bên trái)
        section1 = tk.LabelFrame(left_col, text=f" {self.lang['sections']['quick']} ", 
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.colors['bg'], fg=self.colors['accent_light'],
                                relief='flat', bd=0, labelanchor='n')
        section1.pack(fill='x', pady=(0, 10))

        self.create_modern_button(section1, self.lang['buttons']['upload'], self.upload_code, '🚀', 'success')
        self.create_modern_button(section1, self.lang['buttons']['status'], self.show_git_status, '📊', 'accent')
        self.create_modern_button(section1, self.lang['buttons']['gitignore'], self.create_gitignore, '📝', 'accent')

        # Section: Configuration (bên trái)
        section2 = tk.LabelFrame(left_col, text=f" {self.lang['sections']['config']} ", 
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.colors['bg'], fg=self.colors['accent_light'],
                                relief='flat', bd=0, labelanchor='n')
        section2.pack(fill='x', pady=(0, 10))

        self.create_modern_button(section2, self.lang['buttons']['profiles'], self.manage_profiles, '💾', 'accent')
        self.create_modern_button(section2, self.lang['buttons']['auto_settings'], self.configure_auto, '⏰', 'warning')
        self.create_modern_button(section2, self.lang['buttons']['settings'], self.open_settings, '🎨', 'accent')

        # Section: Background Mode (bên phải)
        section3 = tk.LabelFrame(right_col, text=f" {self.lang['sections']['background']} ", 
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.colors['bg'], fg=self.colors['accent_light'],
                                relief='flat', bd=0, labelanchor='n')
        section3.pack(fill='x', pady=(15, 10))

        self.create_modern_button(section3, self.lang['buttons']['start_bg'], self.start_background, '▶️', 'success')
        self.create_modern_button(section3, self.lang['buttons']['stop_bg'], self.stop_background, '⏸️', 'danger')
        self.create_modern_button(section3, self.lang['buttons']['bg_status'], self.show_bg_status, '📡', 'accent')

        # Section: Utilities (bên phải)
        section4 = tk.LabelFrame(right_col, text=f" {self.lang['sections']['utils']} ", 
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.colors['bg'], fg=self.colors['accent_light'],
                                relief='flat', bd=0, labelanchor='n')
        section4.pack(fill='x', pady=(0, 10))

        self.create_modern_button(section4, self.lang['buttons']['logs'], self.view_logs, '📄', 'accent')
        self.create_modern_button(section4, self.lang['buttons']['exit'], self.quit_application, '🚪', 'danger')

        # Footer with version
        footer = tk.Frame(self.root, bg=self.colors['card'], height=30)
        footer.pack(side='bottom', fill='x')
        footer.pack_propagate(False)
        
        tk.Label(footer, text="© 2025 GitHub Auto Upload Pro v2.4 • Made with 💜", 
                font=('Segoe UI', 7), bg=self.colors['card'], 
                fg=self.colors['fg_secondary']).pack(expand=True)

    def upload_code(self):
        """Upload code với progress window"""
        try:
            progress_win = tk.Toplevel(self.root)
            progress_win.title("Uploading...")
            progress_win.geometry("450x200")
            progress_win.configure(bg=self.colors['bg'])
            progress_win.transient(self.root)
            progress_win.grab_set()
            progress_win.resizable(False, False)
            
            # Center the window
            progress_win.update_idletasks()
            x = (progress_win.winfo_screenwidth() // 2) - (450 // 2)
            y = (progress_win.winfo_screenheight() // 2) - (200 // 2)
            progress_win.geometry(f"450x200+{x}+{y}")
            
            tk.Label(progress_win, text="⏳ Uploading Code...", 
                    font=('Segoe UI', 14, 'bold'),
                    bg=self.colors['bg'], fg=self.colors['accent_light']).pack(pady=30)
            
            status_label = tk.Label(progress_win, text="Preparing...",
                                   font=('Segoe UI', 11),
                                   bg=self.colors['bg'], fg=self.colors['fg'])
            status_label.pack(pady=10)
            
            # Progress bar
            progress = ttk.Progressbar(progress_win, mode='indeterminate', length=350)
            progress.pack(pady=20)
            progress.start(10)
            
            def do_upload():
                try:
                    status_label.config(text="📦 Git add all files...")
                    progress_win.update()
                    time.sleep(0.5)
                    self.uploader.git_add_all()
                    
                    status_label.config(text="💬 Creating commit...")
                    progress_win.update()
                    time.sleep(0.5)
                    self.uploader.git_commit(f"Upload from GUI - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                    
                    status_label.config(text="🚀 Pushing to GitHub...")
                    progress_win.update()
                    time.sleep(0.5)
                    self.uploader.git_push()
                    
                    progress.stop()
                    progress_win.destroy()
                    messagebox.showinfo("✅ Success", "Code uploaded to GitHub successfully!")
                except Exception as e:
                    progress.stop()
                    progress_win.destroy()
                    messagebox.showerror("❌ Error", f"Upload failed:\n\n{str(e)}")
            
            self.root.after(100, do_upload)
            
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
    
    def show_git_status(self):
        """Hiển thị git status"""
        try:
            self.uploader.show_git_status()
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))

    def create_gitignore(self):
        """Tạo .gitignore"""
        try:
            self.uploader.create_gitignore()
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
    
    def manage_profiles(self):
        """Quản lý profiles"""
        try:
            win = tk.Toplevel(self.root)
            win.title("⚙️ Manage Profiles")
            win.geometry("800x550")
            win.configure(bg=self.colors['bg'])
            win.transient(self.root)
            
            # Header
            header = tk.Frame(win, bg=self.colors['accent'], height=70)
            header.pack(fill='x')
            header.pack_propagate(False)
            
            tk.Label(header, text="💾 Profile Manager", 
                    font=('Segoe UI', 16, 'bold'),
                    bg=self.colors['accent'], fg='white').pack(pady=20)
            
            # Main container
            main_container = tk.Frame(win, bg=self.colors['bg'])
            main_container.pack(expand=True, fill='both', padx=20, pady=20)
            
            # Left panel - Profiles list
            left_panel = tk.Frame(main_container, bg=self.colors['card'], 
                                 highlightthickness=2, highlightbackground=self.colors['border'])
            left_panel.pack(side='left', fill='both', padx=(0, 15))
            left_panel.config(width=200)
            
            tk.Label(left_panel, text='📋 Saved Profiles', 
                    font=('Segoe UI', 11, 'bold'),
                    bg=self.colors['card'], fg=self.colors['accent_light']).pack(pady=15)
            
            lb_frame = tk.Frame(left_panel, bg=self.colors['card'])
            lb_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
            
            scrollbar = tk.Scrollbar(lb_frame)
            scrollbar.pack(side='right', fill='y')
            
            lb = tk.Listbox(lb_frame, bg=self.colors['card'], fg=self.colors['fg'],
                           selectbackground=self.colors['accent'], 
                           selectforeground='white',
                           font=('Segoe UI', 10), relief='flat', bd=0,
                           highlightthickness=0, yscrollcommand=scrollbar.set)
            lb.pack(fill='both', expand=True)
            scrollbar.config(command=lb.yview)

            def refresh_list():
                lb.delete(0, 'end')
                for name in self.uploader.list_profiles():
                    lb.insert('end', f"  {name}")

            # Right panel - Edit form
            right_panel = tk.Frame(main_container, bg=self.colors['card'],
                                  highlightthickness=2, highlightbackground=self.colors['border'])
            right_panel.pack(side='left', fill='both', expand=True)

            # Form
            form_frame = tk.Frame(right_panel, bg=self.colors['card'])
            form_frame.pack(padx=20, pady=20, fill='both', expand=True)

            tk.Label(form_frame, text='Profile Details', 
                    font=('Segoe UI', 12, 'bold'),
                    bg=self.colors['card'], fg=self.colors['accent_light']).pack(pady=(0, 15))

            entries = {}
            fields = [
                ('📁 Path', 'path', 45),
                ('🔗 URL', 'url', 45),
                ('🌿 Branch', 'branch', 25),
                ('⏱️ Interval (min)', 'interval', 15),
                ('✏️ Commit Prefix', 'prefix', 35),
            ]

            for label, key, width in fields:
                field_frame = tk.Frame(form_frame, bg=self.colors['card'])
                field_frame.pack(fill='x', pady=8)
                
                tk.Label(field_frame, text=label, font=('Segoe UI', 10),
                        bg=self.colors['card'], fg=self.colors['fg_secondary'], 
                        width=20, anchor='w').pack(side='left')
                
                entry = tk.Entry(field_frame, width=width, bg=self.colors['bg'], 
                               fg=self.colors['fg'],
                               font=('Segoe UI', 10), relief='flat', bd=0,
                               insertbackground=self.colors['accent_light'])
                entry.pack(side='left', padx=5, ipady=6)
                entries[key] = entry

            # Buttons
            button_frame = tk.Frame(form_frame, bg=self.colors['card'])
            button_frame.pack(pady=20, fill='x')

            def create_btn(parent, text, cmd, bg):
                btn = tk.Button(parent, text=text, command=cmd,
                              bg=bg, fg='white',
                              font=('Segoe UI', 9, 'bold'),
                              relief='flat', bd=0, padx=15, pady=8,
                              cursor='hand2')
                return btn

            row1 = tk.Frame(button_frame, bg=self.colors['card'])
            row1.pack(fill='x', pady=5)
            
            def choose_path():
                p = filedialog.askdirectory(title='Select repository folder', 
                                           initialdir=entries['path'].get() or self.uploader.repo_path)
                if p:
                    entries['path'].delete(0, 'end')
                    entries['path'].insert(0, p)
            
            create_btn(row1, '📂 Browse', choose_path, self.colors['accent']).pack(side='left', padx=5)

            def on_save_as():
                name = simpledialog.askstring('Save Profile', 'Profile name:')
                if not name:
                    return
                prof = {
                    'path': entries['path'].get().strip() or self.uploader.repo_path,
                    'url': entries['url'].get().strip() or self.uploader.repo_url,
                    'branch': entries['branch'].get().strip() or self.uploader.branch,
                    'interval': int(entries['interval'].get().strip() or self.uploader.auto_upload_interval or 10),
                    'prefix': entries['prefix'].get().strip() or self.uploader.auto_upload_prefix or 'Auto update',
                }
                self.uploader.save_profile(name, prof)
                refresh_list()
                messagebox.showinfo('✅ Success', f'Profile "{name}" saved!')
            
            create_btn(row1, '💾 Save As', on_save_as, self.colors['success']).pack(side='left', padx=5)

            row2 = tk.Frame(button_frame, bg=self.colors['card'])
            row2.pack(fill='x', pady=5)

            def on_load():
                sel = lb.curselection()
                if not sel:
                    return
                name = lb.get(sel[0]).strip()
                prof = self.uploader.get_profile(name) or {}
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
            
            create_btn(row2, '📥 Load', on_load, self.colors['accent']).pack(side='left', padx=5)

            def on_apply():
                self.uploader.repo_path = entries['path'].get().strip() or self.uploader.repo_path
                self.uploader.repo_url = entries['url'].get().strip() or self.uploader.repo_url
                self.uploader.branch = entries['branch'].get().strip() or self.uploader.branch
                try:
                    self.uploader.auto_upload_interval = int(entries['interval'].get().strip() or self.uploader.auto_upload_interval)
                except:
                    pass
                self.uploader.auto_upload_prefix = entries['prefix'].get().strip() or self.uploader.auto_upload_prefix
                self.uploader.save_config()
                messagebox.showinfo('✅ Success', 'Configuration applied!')
                # Refresh main window info
                win.destroy()
                self.create_widgets()
            
            create_btn(row2, '✅ Apply', on_apply, self.colors['success']).pack(side='left', padx=5)

            def on_delete():
                sel = lb.curselection()
                if not sel:
                    return
                name = lb.get(sel[0]).strip()
                if messagebox.askyesno('Confirm', f'Delete profile "{name}"?'):
                    if self.uploader.delete_profile(name):
                        refresh_list()
                        messagebox.showinfo('✅ Success', f'Profile "{name}" deleted')
            
            create_btn(row2, '🗑️ Delete', on_delete, self.colors['danger']).pack(side='left', padx=5)

            # Load current config
            entries['path'].insert(0, self.uploader.repo_path or '')
            entries['url'].insert(0, self.uploader.repo_url or '')
            entries['branch'].insert(0, self.uploader.branch or '')
            entries['interval'].insert(0, str(self.uploader.auto_upload_interval or 10))
            entries['prefix'].insert(0, self.uploader.auto_upload_prefix or 'Auto update')
            refresh_list()
            
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
    
    def configure_auto(self):
        """Configure auto upload settings"""
        try:
            win = tk.Toplevel(self.root)
            win.title("⏰ Auto Upload Settings")
            win.geometry("500x350")
            win.configure(bg=self.colors['bg'])
            win.transient(self.root)
            win.resizable(False, False)
            
            # Header
            header = tk.Frame(win, bg=self.colors['accent'], height=70)
            header.pack(fill='x')
            header.pack_propagate(False)
            
            tk.Label(header, text="⏰ Auto Upload Configuration", 
                    font=('Segoe UI', 14, 'bold'),
                    bg=self.colors['accent'], fg='white').pack(pady=20)
            
            # Form
            form = tk.Frame(win, bg=self.colors['card'])
            form.pack(expand=True, fill='both', padx=30, pady=30)
            
            tk.Label(form, text="Configure automatic upload interval and settings", 
                    font=('Segoe UI', 10),
                    bg=self.colors['card'], fg=self.colors['fg_secondary']).pack(pady=(0, 20))
            
            # Interval
            interval_frame = tk.Frame(form, bg=self.colors['card'])
            interval_frame.pack(fill='x', pady=10)
            
            tk.Label(interval_frame, text="⏱️ Interval (minutes):", 
                    font=('Segoe UI', 11),
                    bg=self.colors['card'], fg=self.colors['fg']).pack(side='left', padx=10)
            
            interval_var = tk.StringVar(value=str(self.uploader.auto_upload_interval))
            interval_entry = tk.Entry(interval_frame, textvariable=interval_var,
                                     width=10, bg=self.colors['bg'], fg=self.colors['fg'],
                                     font=('Segoe UI', 11), relief='flat', bd=0,
                                     insertbackground=self.colors['accent_light'])
            interval_entry.pack(side='left', padx=10, ipady=5)
            
            # Prefix
            prefix_frame = tk.Frame(form, bg=self.colors['card'])
            prefix_frame.pack(fill='x', pady=10)
            
            tk.Label(prefix_frame, text="✏️ Commit prefix:", 
                    font=('Segoe UI', 11),
                    bg=self.colors['card'], fg=self.colors['fg']).pack(side='left', padx=10)
            
            prefix_var = tk.StringVar(value=self.uploader.auto_upload_prefix)
            prefix_entry = tk.Entry(prefix_frame, textvariable=prefix_var,
                                   width=30, bg=self.colors['bg'], fg=self.colors['fg'],
                                   font=('Segoe UI', 11), relief='flat', bd=0,
                                   insertbackground=self.colors['accent_light'])
            prefix_entry.pack(side='left', padx=10, ipady=5)
            
            # Save button
            def save_settings():
                try:
                    self.uploader.auto_upload_interval = int(interval_var.get())
                    self.uploader.auto_upload_prefix = prefix_var.get()
                    self.uploader.save_config()
                    messagebox.showinfo('✅ Success', 'Settings saved!')
                    win.destroy()
                except ValueError:
                    messagebox.showerror('❌ Error', 'Invalid interval value')
            
            btn_frame = tk.Frame(form, bg=self.colors['card'])
            btn_frame.pack(pady=30)
            
            tk.Button(btn_frame, text="💾 Save Settings", command=save_settings,
                     bg=self.colors['success'], fg='white',
                     font=('Segoe UI', 11, 'bold'),
                     relief='flat', bd=0, padx=30, pady=10,
                     cursor='hand2').pack()
            
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
    
    def open_settings(self):
        """Open settings window"""
        try:
            win = tk.Toplevel(self.root)
            win.title("🎨 Settings")
            win.geometry("700x650")
            win.configure(bg=self.colors['bg'])
            win.transient(self.root)
            win.resizable(False, True)
            win.minsize(700, 550)
            
            # Header
            header = tk.Frame(win, bg=self.colors['accent'], height=70)
            header.pack(fill='x')
            header.pack_propagate(False)
            
            tk.Label(header, text=self.lang['buttons']['settings'], 
                    font=('Segoe UI', 16, 'bold'),
                    bg=self.colors['accent'], fg='white').pack(pady=20)
            
            # Scrollable container
            canvas_container = tk.Frame(win, bg=self.colors['bg'])
            canvas_container.pack(expand=True, fill='both', padx=10, pady=10)
            
            canvas = tk.Canvas(canvas_container, bg=self.colors['bg'], highlightthickness=0)
            scrollbar = tk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
            scrollable_form = tk.Frame(canvas, bg=self.colors['card'])
            
            scrollable_form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            
            canvas.create_window((0, 0), window=scrollable_form, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Mouse wheel scrolling
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind("<MouseWheel>", _on_mousewheel)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Form
            form = scrollable_form
            
            # Theme selection
            theme_frame = tk.Frame(form, bg=self.colors['card'])
            theme_frame.pack(fill='x', pady=(20, 15), padx=20)
            
            tk.Label(theme_frame, text=f"🎨 {self.lang['settings']['theme']}:", 
                    font=('Segoe UI', 11, 'bold'),
                    bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w', pady=(0, 10))
            
            theme_var = tk.StringVar(value=getattr(self.uploader, 'theme', 'github_dark'))
            
            themes_data = [
                ('GitHub Dark', 'github_dark'),
                ('Blue Dark', 'blue_dark'),
                ('Purple Dark', 'purple_dark'),
                ('Light White', 'light_white')
            ]
            
            for name, value in themes_data:
                rb = tk.Radiobutton(theme_frame, text=name, variable=theme_var, value=value,
                                   bg=self.colors['card'], fg=self.colors['fg'],
                                   selectcolor=self.colors['bg'],
                                   activebackground=self.colors['card'],
                                   activeforeground=self.colors['accent_light'],
                                   font=('Segoe UI', 10))
                rb.pack(anchor='w', pady=3)
            
            # Language selection
            lang_frame = tk.Frame(form, bg=self.colors['card'])
            lang_frame.pack(fill='x', pady=15, padx=20)
            
            tk.Label(lang_frame, text=f"🌐 {self.lang['settings']['language']}:", 
                    font=('Segoe UI', 11, 'bold'),
                    bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w', pady=(0, 10))
            
            lang_var = tk.StringVar(value=getattr(self.uploader, 'language', 'vi'))
            
            langs_data = [
                ('Tiếng Việt', 'vi'),
                ('English', 'en')
            ]
            
            for name, value in langs_data:
                rb = tk.Radiobutton(lang_frame, text=name, variable=lang_var, value=value,
                                   bg=self.colors['card'], fg=self.colors['fg'],
                                   selectcolor=self.colors['bg'],
                                   activebackground=self.colors['card'],
                                   activeforeground=self.colors['accent_light'],
                                   font=('Segoe UI', 10))
                rb.pack(anchor='w', pady=3)
            
            # System Tray toggle
            tray_frame = tk.Frame(form, bg=self.colors['card'])
            tray_frame.pack(fill='x', pady=15, padx=20)
            
            tk.Label(tray_frame, text=f"🔔 {self.lang['settings']['tray']}:", 
                    font=('Segoe UI', 11, 'bold'),
                    bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w', pady=(0, 10))
            
            tray_var = tk.BooleanVar(value=getattr(self.uploader, 'enable_tray', True))
            tray_cb = tk.Checkbutton(tray_frame, text=self.lang['settings']['enable_tray'], variable=tray_var,
                                     bg=self.colors['card'], fg=self.colors['fg'],
                                     selectcolor=self.colors['bg'],
                                     activebackground=self.colors['card'],
                                     activeforeground=self.colors['accent_light'],
                                     font=('Segoe UI', 10))
            tray_cb.pack(anchor='w', pady=3)
            
            # Auto start toggle
            auto_start_frame = tk.Frame(form, bg=self.colors['card'])
            auto_start_frame.pack(fill='x', pady=15, padx=20)
            
            tk.Label(auto_start_frame, text="🚀 Startup:", 
                    font=('Segoe UI', 11, 'bold'),
                    bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w', pady=(0, 10))
            
            auto_start_var = tk.BooleanVar(value=getattr(self.uploader, 'auto_start', False))
            auto_start_cb = tk.Checkbutton(auto_start_frame, 
                                          text=self.lang['settings'].get('auto_start', 'Start with Windows'),
                                          variable=auto_start_var,
                                          bg=self.colors['card'], fg=self.colors['fg'],
                                          selectcolor=self.colors['bg'],
                                          activebackground=self.colors['card'],
                                          activeforeground=self.colors['accent_light'],
                                          font=('Segoe UI', 10))
            auto_start_cb.pack(anchor='w', pady=3)
            
            # Auto update notification
            auto_update_frame = tk.Frame(form, bg=self.colors['card'])
            auto_update_frame.pack(fill='x', pady=15, padx=20)
            
            tk.Label(auto_update_frame, text="⚡ Auto Update Notifications:", 
                    font=('Segoe UI', 11, 'bold'),
                    bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w', pady=(0, 10))
            
            auto_update_var = tk.BooleanVar(value=getattr(self.uploader, 'auto_update_notify', True))
            auto_update_cb = tk.Checkbutton(auto_update_frame, 
                                           text=self.lang['settings'].get('auto_update_notify', 'Show notifications for auto updates'),
                                           variable=auto_update_var,
                                           bg=self.colors['card'], fg=self.colors['fg'],
                                           selectcolor=self.colors['bg'],
                                           activebackground=self.colors['card'],
                                           activeforeground=self.colors['accent_light'],
                                           font=('Segoe UI', 10))
            auto_update_cb.pack(anchor='w', pady=3)
            
            # Save button
            btn_frame = tk.Frame(form, bg=self.colors['card'])
            btn_frame.pack(pady=30, padx=20)
            
            def save_settings():
                try:
                    self.uploader.theme = theme_var.get()
                    self.uploader.language = lang_var.get()
                    self.uploader.enable_tray = tray_var.get()
                    self.uploader.auto_start = auto_start_var.get()
                    self.uploader.auto_update_notify = auto_update_var.get()
                    self.uploader.save_config()
                    
                    # Toggle auto start
                    self.toggle_auto_start(auto_start_var.get())
                    
                    messagebox.showinfo('✅ Success', 'Settings saved!\nApplication will restart to apply changes.')
                    win.destroy()
                    self.quit_application()
                except Exception as e:
                    messagebox.showerror('❌ Error', f'Failed to save settings: {str(e)}')
            
            tk.Button(btn_frame, text=f"💾 {self.lang['settings']['save']}", command=save_settings,
                     bg=self.colors['success'], fg='white',
                     font=('Segoe UI', 11, 'bold'),
                     relief='flat', bd=0, padx=30, pady=10,
                     cursor='hand2').pack()
            
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
    
    def toggle_auto_start(self, enable):
        """Enable or disable auto start with Windows"""
        try:
            if sys.platform.startswith('win'):
                import winreg
                app_name = "GitHub Auto Upload Pro"
                key = winreg.HKEY_CURRENT_USER
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                
                try:
                    with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as regkey:
                        if enable:
                            script_path = os.path.abspath(__file__)
                            winreg.SetValueEx(regkey, app_name, 0, winreg.REG_SZ, 
                                            f'"{sys.executable}" "{script_path}"')
                        else:
                            try:
                                winreg.DeleteValue(regkey, app_name)
                            except FileNotFoundError:
                                pass
                except Exception as e:
                    self.logger.warning(f"Could not modify registry: {e}")
        except Exception as e:
            self.logger.error(f"Failed to toggle auto start: {e}")

    def start_background(self):
        """Start background mode"""
        try:
            self.uploader.start_background_mode()
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))

    def stop_background(self):
        """Stop background mode"""
        try:
            ok = self.uploader.stop_background_mode()
            if ok:
                messagebox.showinfo("✅ Success", "Background process stopped")
            else:
                messagebox.showinfo("ℹ️ Info", "No background process found")
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))

    def show_bg_status(self):
        """Show background status window"""
        try:
            win = tk.Toplevel(self.root)
            win.title("📡 Background Status")
            win.geometry("700x500")
            win.configure(bg=self.colors['bg'])
            win.transient(self.root)
            
            # Header
            header = tk.Frame(win, bg=self.colors['accent'], height=70)
            header.pack(fill='x')
            header.pack_propagate(False)
            
            tk.Label(header, text="📡 Background Service Monitor", 
                    font=('Segoe UI', 14, 'bold'),
                    bg=self.colors['accent'], fg='white').pack(pady=20)
            
            # Main container
            container = tk.Frame(win, bg=self.colors['bg'])
            container.pack(expand=True, fill='both', padx=20, pady=20)
            
            # Action bar
            action_bar = tk.Frame(container, bg=self.colors['card'],
                                 highlightthickness=2, highlightbackground=self.colors['border'])
            action_bar.pack(fill='x', pady=(0, 15))
            
            action_inner = tk.Frame(action_bar, bg=self.colors['card'])
            action_inner.pack(padx=15, pady=12)
            
            refresh_btn = tk.Button(action_inner, text="🔄 Refresh", 
                                   bg=self.colors['accent'], fg='white',
                                   font=('Segoe UI', 9, 'bold'), relief='flat',
                                   padx=15, pady=6, cursor='hand2',
                                   activebackground=self.colors['accent_light'])
            refresh_btn.pack(side='left', padx=5)

            # Status display
            status_frame = tk.Frame(container, bg=self.colors['card'],
                                   highlightthickness=2, highlightbackground=self.colors['border'])
            status_frame.pack(expand=True, fill='both')
            
            status_inner = tk.Frame(status_frame, bg=self.colors['card'])
            status_inner.pack(padx=25, pady=25, fill='both', expand=True)
            
            labels = {}
            fields = [
                ('🆔 Process ID', 'pid'),
                ('▶️ Running Status', 'running'),
                ('🕐 Last Update', 'timestamp'),
                ('📊 Result', 'result'),
                ('💬 Message', 'message'),
                ('📁 Repository', 'path'),
                ('🌿 Branch', 'branch'),
                ('⏱️ Interval (min)', 'interval'),
                ('✏️ Commit Prefix', 'prefix'),
            ]
            
            for title, key in fields:
                row = tk.Frame(status_inner, bg=self.colors['card'])
                row.pack(fill='x', pady=8)
                
                tk.Label(row, text=title, font=('Segoe UI', 10),
                        bg=self.colors['card'], fg=self.colors['fg_secondary'],
                        width=22, anchor='w').pack(side='left')
                
                val = tk.Label(row, text='Loading...', font=('Segoe UI', 10, 'bold'),
                              bg=self.colors['card'], fg=self.colors['fg'],
                              anchor='w')
                val.pack(side='left', fill='x', expand=True)
                labels[key] = val

            def do_refresh():
                pid = self.uploader._read_bg_pid()
                running = self.uploader.is_background_running()
                st = self.uploader.read_status() or {}
                
                labels['pid'].config(text=str(pid or 'N/A'))
                
                if running:
                    labels['running'].config(text='✅ Active', fg=self.colors['success'])
                else:
                    labels['running'].config(text='❌ Inactive', fg=self.colors['danger'])
                
                labels['timestamp'].config(text=st.get('timestamp', 'N/A'))
                
                result = st.get('result', 'N/A')
                if result == 'success':
                    labels['result'].config(text=f'✅ {result}', fg=self.colors['success'])
                elif result == 'failure':
                    labels['result'].config(text=f'❌ {result}', fg=self.colors['danger'])
                else:
                    labels['result'].config(text=f'ℹ️ {result}', fg=self.colors['warning'])
                
                labels['message'].config(text=st.get('message', 'N/A'))
                labels['path'].config(text=st.get('path', 'N/A'))
                labels['branch'].config(text=st.get('branch', 'N/A'))
                labels['interval'].config(text=str(st.get('interval', 'N/A')))
                labels['prefix'].config(text=st.get('prefix', 'N/A'))

            def auto_refresh():
                do_refresh()
                win.after(3000, auto_refresh)

            refresh_btn.config(command=do_refresh)
            do_refresh()
            auto_refresh()
            
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))

    def view_logs(self):
        """View logs"""
        try:
            self.uploader.view_logs()
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))

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
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Auto Upload Tool Pro
Công cụ tự động đẩy code lên GitHub với nhiều tính năng nâng cao
Version 4.0 - Ultimate Edition with Security & Notifications
"""

import os
import sys
import subprocess
import json
import logging
import time
import psutil
import base64
import hashlib
import winreg
from datetime import datetime
from pathlib import Path
from threading import Thread
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, scrolledtext
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from cryptography.fernet import Fernet
from plyer import notification


# Language translations
TRANSLATIONS = {
    'en': {
        'app_title': 'GitHub Auto Upload Tool Pro',
        'quick_actions': '⚡ Quick Actions',
        'upload': '🚀 Upload to GitHub',
        'git_status': '📊 Git Status',
        'create_gitignore': '📝 Create .gitignore',
        'configuration': '⚙️ Configuration',
        'manage_profiles': '💾 Manage Profiles',
        'auto_settings': '⏰ Auto Upload Settings',
        'commit_mode': '📋 Commit Mode',
        'background_mode': '🔄 Background Mode',
        'start_bg': '▶️ Start Background',
        'stop_bg': '⏸️ Stop Background',
        'view_status': '📡 View Status',
        'utilities': '🛠️ Utilities',
        'view_logs': '📄 View Logs',
        'exit': '🚪 Exit',
        'settings': '⚙️ Settings',
        'success': '✅ Success',
        'error': '❌ Error',
        'warning': '⚠️ Warning',
        'confirm': '❓ Confirm',
        'info': 'ℹ️ Info',
        'uploading': 'Uploading to GitHub...',
        'pulling': 'Pulling latest changes...',
        'pushing': 'Pushing to remote...',
        'upload_success': 'Upload successful!',
        'upload_failed': 'Upload failed',
        'bg_started': 'Background mode started!',
        'bg_stopped': 'Background mode stopped!',
        'minimize_info': 'App minimized to system tray.\nRight-click tray icon to access menu.',
    },
    'vi': {
        'app_title': 'Công cụ Tự động Upload GitHub Pro',
        'quick_actions': '⚡ Thao tác Nhanh',
        'upload': '🚀 Upload lên GitHub',
        'git_status': '📊 Trạng thái Git',
        'create_gitignore': '📝 Tạo .gitignore',
        'configuration': '⚙️ Cấu hình',
        'manage_profiles': '💾 Quản lý Profiles',
        'auto_settings': '⏰ Cài đặt Tự động',
        'commit_mode': '📋 Chế độ Commit',
        'background_mode': '🔄 Chế độ Nền',
        'start_bg': '▶️ Khởi động Nền',
        'stop_bg': '⏸️ Dừng Nền',
        'view_status': '📡 Xem Trạng thái',
        'utilities': '🛠️ Tiện ích',
        'view_logs': '📄 Xem Logs',
        'exit': '🚪 Thoát',
        'settings': '⚙️ Cài đặt',
        'success': '✅ Thành công',
        'error': '❌ Lỗi',
        'warning': '⚠️ Cảnh báo',
        'confirm': '❓ Xác nhận',
        'info': 'ℹ️ Thông tin',
        'uploading': 'Đang upload lên GitHub...',
        'pulling': 'Đang kéo thay đổi mới nhất...',
        'pushing': 'Đang đẩy lên remote...',
        'upload_success': 'Upload thành công!',
        'upload_failed': 'Upload thất bại',
        'bg_started': 'Chế độ nền đã khởi động!',
        'bg_stopped': 'Chế độ nền đã dừng!',
        'minimize_info': 'Ứng dụng đã thu nhỏ vào khay hệ thống.\nNhấp chuột phải vào biểu tượng để truy cập menu.',
    }
}

# Predefined themes
THEMES = {
    'GitHub Dark': {
        'bg': '#0d1117',
        'card': '#161b22',
        'border': '#30363d',
        'fg': '#c9d1d9',
        'fg_secondary': '#8b949e',
        'fg_tertiary': '#6e7681',
        'accent': '#58a6ff',
        'success': '#3fb950',
        'warning': '#d29922',
        'danger': '#f85149'
    },
    'GitHub Light': {
        'bg': '#ffffff',
        'card': '#f6f8fa',
        'border': '#d0d7de',
        'fg': '#24292f',
        'fg_secondary': '#57606a',
        'fg_tertiary': '#6e7781',
        'accent': '#0969da',
        'success': '#1a7f37',
        'warning': '#9a6700',
        'danger': '#d1242f'
    },
    'Dark Blue': {
        'bg': '#1a1d2e',
        'card': '#252837',
        'border': '#2f3349',
        'fg': '#e4e6eb',
        'fg_secondary': '#9ca3af',
        'fg_tertiary': '#6b7280',
        'accent': '#3b82f6',
        'success': '#10b981',
        'warning': '#f59e0b',
        'danger': '#ef4444'
    },
    'Purple Night': {
        'bg': '#1e1b2e',
        'card': '#2a2740',
        'border': '#3a3553',
        'fg': '#e0def4',
        'fg_secondary': '#908caa',
        'fg_tertiary': '#6e6a86',
        'accent': '#9d7cd8',
        'success': '#7aa89f',
        'warning': '#ffa066',
        'danger': '#f47171'
    },
    'Ocean Breeze': {
        'bg': '#0a1929',
        'card': '#1a2332',
        'border': '#2a3645',
        'fg': '#d6e4ff',
        'fg_secondary': '#a8c7fa',
        'fg_tertiary': '#7a9fd8',
        'accent': '#3399ff',
        'success': '#00bfa5',
        'warning': '#ffab00',
        'danger': '#ff5252'
    }
}


class SecurityManager:
    """Quản lý bảo mật và mã hóa"""
    
    def __init__(self):
        self.key_file = Path.home() / '.github_uploader' / '.key'
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self):
        """Tạo hoặc lấy key mã hóa"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt(self, text: str) -> str:
        """Mã hóa văn bản"""
        try:
            return self.cipher.encrypt(text.encode()).decode()
        except:
            return text
    
    def decrypt(self, encrypted_text: str) -> str:
        """Giải mã văn bản"""
        try:
            return self.cipher.decrypt(encrypted_text.encode()).decode()
        except:
            return encrypted_text
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash mật khẩu"""
        return hashlib.sha256(password.encode()).hexdigest()


class NotificationManager:
    """Quản lý thông báo hệ thống"""
    
    def __init__(self, app_name: str = "GitHub Uploader"):
        self.app_name = app_name
    
    def send(self, title: str, message: str, timeout: int = 5):
        """Gửi thông báo"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                timeout=timeout,
                app_icon=None
            )
        except Exception as e:
            print(f"Notification error: {e}")


class GitHubUploader:
    """Core class xử lý Git operations"""
    
    def __init__(self):
        self.config_file = Path.home() / '.github_uploader' / 'config.json'
        self.profiles_file = Path.home() / '.github_uploader' / 'profiles.json'
        self.log_dir = Path.home() / '.github_uploader' / 'logs'
        self.status_file = Path.home() / '.github_uploader' / 'status.json'
        self.bg_pid_file = Path.home() / '.github_uploader' / 'background.pid'
        self.settings_file = Path.home() / '.github_uploader' / 'settings.json'
        self.auth_file = Path.home() / '.github_uploader' / 'auth.json'
        
        # Tạo thư mục config
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Security & Notification
        self.security = SecurityManager()
        self.notifier = NotificationManager()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / f'upload_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load settings & config
        self.load_settings()
        self.load_config()
        self.load_auth()

    def load_settings(self):
        """Load app settings"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.minimize_to_tray = settings.get('minimize_to_tray', True)
                    self.show_notifications = settings.get('show_notifications', True)
                    self.play_sound = settings.get('play_sound', False)
                    self.start_with_windows = settings.get('start_with_windows', False)
                    self.start_minimized = settings.get('start_minimized', False)
                    self.theme_name = settings.get('theme_name', 'GitHub Dark')
                    self.custom_theme = settings.get('custom_theme', None)
                    self.language = settings.get('language', 'en')
                    self.silent_mode = settings.get('silent_mode', False)
                    self.auto_pull = settings.get('auto_pull', True)
                    self.auto_resolve = settings.get('auto_resolve', True)
                    self.app_password = settings.get('app_password', None)
                    self.remember_credentials = settings.get('remember_credentials', False)
            else:
                self.minimize_to_tray = True
                self.show_notifications = True
                self.play_sound = False
                self.start_with_windows = False
                self.start_minimized = False
                self.theme_name = 'GitHub Dark'
                self.custom_theme = None
                self.language = 'en'
                self.silent_mode = False
                self.auto_pull = True
                self.auto_resolve = True
                self.app_password = None
                self.remember_credentials = False
                self.save_settings()
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")

    def save_settings(self):
        """Save app settings"""
        try:
            settings = {
                'minimize_to_tray': self.minimize_to_tray,
                'show_notifications': self.show_notifications,
                'play_sound': self.play_sound,
                'start_with_windows': self.start_with_windows,
                'start_minimized': self.start_minimized,
                'theme_name': self.theme_name,
                'custom_theme': self.custom_theme,
                'language': self.language,
                'silent_mode': self.silent_mode,
                'auto_pull': self.auto_pull,
                'auto_resolve': self.auto_resolve,
                'app_password': self.app_password,
                'remember_credentials': self.remember_credentials
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            
            # Update startup
            self._update_windows_startup()
            
            self.logger.info("Settings saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")

    def load_auth(self):
        """Load authentication"""
        try:
            if self.auth_file.exists() and self.remember_credentials:
                with open(self.auth_file, 'r', encoding='utf-8') as f:
                    auth = json.load(f)
                    self.github_token = self.security.decrypt(auth.get('token', ''))
                    self.github_username = self.security.decrypt(auth.get('username', ''))
            else:
                self.github_token = ''
                self.github_username = ''
        except Exception as e:
            self.logger.error(f"Error loading auth: {e}")
            self.github_token = ''
            self.github_username = ''

    def save_auth(self):
        """Save authentication"""
        try:
            if self.remember_credentials:
                auth = {
                    'token': self.security.encrypt(self.github_token),
                    'username': self.security.encrypt(self.github_username)
                }
                with open(self.auth_file, 'w', encoding='utf-8') as f:
                    json.dump(auth, f, indent=4)
            else:
                if self.auth_file.exists():
                    self.auth_file.unlink()
        except Exception as e:
            self.logger.error(f"Error saving auth: {e}")

    def _update_windows_startup(self):
        """Cập nhật startup với Windows"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "GitHubAutoUpload"
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            
            if self.start_with_windows:
                exe_path = sys.executable
                script_path = os.path.abspath(__file__)
                value = f'"{exe_path}" "{script_path}"'
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, value)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except:
                    pass
            
            winreg.CloseKey(key)
        except Exception as e:
            self.logger.error(f"Error updating startup: {e}")

    def load_config(self):
        """Load cấu hình từ file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.repo_path = config.get('repo_path', '')
                    self.remote_url = config.get('remote_url', '')
                    self.branch = config.get('branch', 'main')
                    self.auto_upload_interval = config.get('auto_upload_interval', 30)
                    self.commit_message_template = config.get('commit_message_template', 
                                                             'Update: {datetime}')
                    self.current_profile = config.get('current_profile', 'default')
                    self.commit_mode = config.get('commit_mode', 'always')
                    self.last_commit_date = config.get('last_commit_date', '')
                    self.use_conventional_commits = config.get('use_conventional_commits', False)
            else:
                self.repo_path = ''
                self.remote_url = ''
                self.branch = 'main'
                self.auto_upload_interval = 30
                self.commit_message_template = 'Update: {datetime}'
                self.current_profile = 'default'
                self.commit_mode = 'always'
                self.last_commit_date = ''
                self.use_conventional_commits = False
                self.save_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")

    def save_config(self):
        """Lưu cấu hình vào file"""
        try:
            config = {
                'repo_path': self.repo_path,
                'remote_url': self.remote_url,
                'branch': self.branch,
                'auto_upload_interval': self.auto_upload_interval,
                'commit_message_template': self.commit_message_template,
                'current_profile': self.current_profile,
                'commit_mode': self.commit_mode,
                'last_commit_date': self.last_commit_date,
                'use_conventional_commits': self.use_conventional_commits
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.logger.info("Config saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    def run_command(self, command: str):
        """Chạy command và trả về output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.repo_path if self.repo_path else None,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                self.logger.error(f"Command failed: {result.stderr}")
                return None
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timeout: {command}")
            return None
        except Exception as e:
            self.logger.error(f"Error running command: {e}")
            return None

    def _git(self, args: str):
        """Wrapper cho git commands"""
        return self.run_command(f"git {args}")

    def git_pull(self) -> bool:
        """Git pull từ remote"""
        try:
            if not self.auto_pull:
                return True
            
            self.logger.info("Pulling latest changes...")
            result = self._git(f"pull origin {self.branch}")
            
            if result is None:
                # Có conflict
                if self.auto_resolve:
                    self.logger.info("Attempting auto-resolve...")
                    self._git("checkout --ours .")
                    self._git("add .")
                    return True
                return False
            
            self.logger.info("Pull successful")
            return True
        except Exception as e:
            self.logger.error(f"Error pulling: {e}")
            return False

    def show_git_status(self):
        """Hiển thị Git status"""
        try:
            status = self._git("status")
            if status:
                messagebox.showinfo("Git Status", status)
            else:
                messagebox.showerror("Error", "Cannot get Git status")
        except Exception as e:
            self.logger.error(f"Error showing status: {e}")
            messagebox.showerror("Error", str(e))

    def create_gitignore(self):
        """Tạo file .gitignore"""
        try:
            if not self.repo_path:
                messagebox.showerror("Error", "Repository not configured!")
                return
            
            gitignore_path = Path(self.repo_path) / '.gitignore'
            default_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Config
config.json
*.env
"""
            
            if gitignore_path.exists():
                response = messagebox.askyesno("Confirm", 
                    ".gitignore already exists. Overwrite?")
                if not response:
                    return
            
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(default_content)
            
            messagebox.showinfo("Success", ".gitignore created")
            self.logger.info(".gitignore created")
        except Exception as e:
            self.logger.error(f"Error creating .gitignore: {e}")
            messagebox.showerror("Error", str(e))

    def git_add_all(self) -> bool:
        """Git add tất cả files"""
        try:
            result = self._git("add .")
            return result is not None or True
        except Exception as e:
            self.logger.error(f"Error adding files: {e}")
            return False

    def git_commit(self, message: str) -> bool:
        """Git commit với message"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            if self.commit_mode == 'daily':
                if self.last_commit_date == today:
                    self.logger.info("Already committed today (daily mode)")
                    return False
            elif self.commit_mode == 'manual':
                self.logger.info("Manual mode - skipping auto commit")
                return False
            
            if not message:
                message = self.commit_message_template.format(
                    datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    date=datetime.now().strftime("%Y-%m-%d"),
                    time=datetime.now().strftime("%H:%M:%S"),
                    user=os.environ.get('USERNAME', 'user')
                )
            
            result = self._git(f'commit -m "{message}"')
            if result is not None:
                self.last_commit_date = today
                self.save_config()
                self.logger.info(f"Committed: {message}")
                
                # Notification
                if self.show_notifications and not self.silent_mode:
                    self.notifier.send("Commit Success", f"Committed: {message[:50]}...")
                
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error committing: {e}")
            if self.show_notifications and not self.silent_mode:
                self.notifier.send("Commit Failed", str(e))
            return False

    def git_push(self) -> bool:
        """Git push lên remote"""
        try:
            result = self._git(f"push -u origin {self.branch}")
            if result is not None:
                self.logger.info(f"Pushed to {self.branch}")
                
                # Notification
                if self.show_notifications and not self.silent_mode:
                    self.notifier.send("Push Success", f"Pushed to {self.branch}")
                
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error pushing: {e}")
            if self.show_notifications and not self.silent_mode:
                self.notifier.send("Push Failed", str(e))
            return False

    def start_background_mode(self) -> bool:
        """Start background upload mode"""
        try:
            if self.is_background_running():
                return False
            
            thread = Thread(target=self.run_background_loop, daemon=True)
            thread.start()
            
            with open(self.bg_pid_file, 'w') as f:
                f.write(str(os.getpid()))
            
            self.logger.info("Background mode started")
            
            if self.show_notifications and not self.silent_mode:
                self.notifier.send("Background Started", "Auto upload mode activated")
            
            return True
        except Exception as e:
            self.logger.error(f"Error starting background mode: {e}")
            return False

    def stop_background_mode(self) -> bool:
        """Stop background upload mode"""
        try:
            if self.bg_pid_file.exists():
                self.bg_pid_file.unlink()
                self.logger.info("Background mode stopped")
                
                if self.show_notifications and not self.silent_mode:
                    self.notifier.send("Background Stopped", "Auto upload mode deactivated")
                
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error stopping background mode: {e}")
            return False

    def is_background_running(self) -> bool:
        """Kiểm tra background mode có đang chạy không"""
        try:
            if self.bg_pid_file.exists():
                with open(self.bg_pid_file, 'r') as f:
                    pid = int(f.read().strip())
                return psutil.pid_exists(pid)
            return False
        except:
            return False

    def run_background_loop(self):
        """Background loop để auto upload"""
        self.logger.info("Background loop started")
        while self.is_background_running():
            try:
                if self.repo_path and Path(self.repo_path).exists():
                    status = self._git("status --porcelain")
                    if status:
                        self.logger.info("Changes detected, uploading...")
                        
                        # Pull first
                        if not self.git_pull():
                            self._write_status("error", "Pull failed")
                            continue
                        
                        if self.git_add_all():
                            if self.git_commit(""):
                                if self.git_push():
                                    self._write_status("success", "Auto upload successful")
                                else:
                                    self._write_status("error", "Push failed")
                            else:
                                self._write_status("info", "No changes to commit or daily limit reached")
                        else:
                            self._write_status("error", "Add failed")
                    else:
                        self._write_status("info", "No changes detected")
                
                time.sleep(self.auto_upload_interval * 60)
            except Exception as e:
                self.logger.error(f"Background loop error: {e}")
                self._write_status("error", str(e))
                time.sleep(60)

    def _write_status(self, result: str, message: str = ""):
        """Ghi status vào file"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'result': result,
                'message': message
            }
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error writing status: {e}")

    def read_status(self):
        """Đọc status từ file"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.error(f"Error reading status: {e}")
            return None

    def view_logs(self):
        """Xem logs"""
        try:
            import webbrowser
            log_files = list(self.log_dir.glob('*.log'))
            if log_files:
                latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
                webbrowser.open(str(latest_log))
            else:
                messagebox.showinfo("Info", "No log files found")
        except Exception as e:
            self.logger.error(f"Error viewing logs: {e}")
            messagebox.showerror("Error", str(e))


class SystemTrayManager:
    """Quản lý System Tray"""
    
    def __init__(self, gui_app):
        self.gui_app = gui_app
        self.icon = None
        
    def create_image(self):
        """Tạo icon cho system tray"""
        width = 64
        height = 64
        color = self.gui_app.colors['accent'] if hasattr(self.gui_app, 'colors') else '#58a6ff'
        image = Image.new('RGB', (width, height), color=color)
        dc = ImageDraw.Draw(image)
        dc.text((10, 20), "GH", fill='white')
        return image
    
    def show_window(self, icon=None, item=None):
        """Hiển thị cửa sổ chính"""
        self.gui_app.root.deiconify()
        self.gui_app.root.lift()
        self.gui_app.root.focus_force()
    
    def hide_window(self):
        """Ẩn cửa sổ chính"""
        self.gui_app.root.withdraw()
    
    def quit_app(self, icon=None, item=None):
        """Thoát ứng dụng"""
        if icon:
            icon.stop()
        self.gui_app.root.quit()
        sys.exit(0)
    
    def start(self):
        """Khởi động system tray"""
        menu = (
            item('Show Window', self.show_window),
            item('Quit', self.quit_app)
        )
        
        self.icon = pystray.Icon(
            "GitHub Uploader",
            self.create_image(),
            "GitHub Auto Upload Tool",
            menu
        )
        
        Thread(target=self.icon.run, daemon=True).start()


class GitHubUploaderGUI:
    """GUI class cho ứng dụng"""
    
    def __init__(self):
        self.root = tk.Tk()
        
        # Initialize uploader
        self.uploader = GitHubUploader()
        
        # Check app password
        if self.uploader.app_password and not self._verify_app_password():
            self.root.destroy()
            sys.exit(0)
        
        # Setup window
        self.root.title(self.t('app_title') + " v4.0")
        self.root.geometry("950x750")
        
        # Apply theme
        self.apply_theme()
        
        # System tray
        self.tray_manager = SystemTrayManager(self)
        
        # Create GUI
        self.create_widgets()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start system tray
        self.tray_manager.start()
        
        # Start minimized if enabled
        if self.uploader.start_minimized:
            self.root.withdraw()

    def t(self, key: str) -> str:
        """Translate text"""
        return TRANSLATIONS.get(self.uploader.language, TRANSLATIONS['en']).get(key, key)

    def _verify_app_password(self) -> bool:
        """Verify app password"""
        password = simpledialog.askstring("Password", "Enter app password:", show='*')
        if not password:
            return False
        return self.uploader.security.hash_password(password) == self.uploader.app_password

    def apply_theme(self):
        """Apply current theme"""
        if self.uploader.custom_theme:
            self.colors = self.uploader.custom_theme
        else:
            self.colors = THEMES.get(self.uploader.theme_name, THEMES['GitHub Dark'])
        
        self.root.configure(bg=self.colors['bg'])

    def create_widgets(self):
        """Tạo giao diện"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.root, bg=self.colors['accent'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=self.colors['accent'])
        header_content.pack(expand=True)
        
        tk.Label(header_content, text="🚀 GitHub Auto Upload Tool Pro", 
                font=('Segoe UI', 18, 'bold'), bg=self.colors['accent'], 
                fg='white').pack(side='left', padx=20)
        
        # Settings button in header
        settings_btn = tk.Button(header_content, text="⚙️ Settings", 
                                 command=self.open_advanced_settings,
                                 bg=self.colors['bg'], fg=self.colors['fg'],
                                 font=('Segoe UI', 10, 'bold'), relief='flat',
                                 cursor='hand2', padx=15, pady=8)
        settings_btn.pack(side='right', padx=20)
        
        # Info card
        info_card = tk.Frame(self.root, bg=self.colors['card'])
        info_card.pack(fill='x', padx=20, pady=15)
        
        info_content = tk.Frame(info_card, bg=self.colors['card'])
        info_content.pack(padx=15, pady=12)
        
        repo_text = self.uploader.repo_path if self.uploader.repo_path else "Not configured"
        if len(repo_text) > 60:
            repo_text = "..." + repo_text[-57:]
        
        tk.Label(info_content, text=f"📁 {repo_text}", 
                font=('Segoe UI', 10), bg=self.colors['card'], 
                fg=self.colors['fg']).pack(anchor='w', pady=2)
        
        tk.Label(info_content, text=f"🌿 Branch: {self.uploader.branch} | 🎨 Theme: {self.uploader.theme_name}", 
                font=('Segoe UI', 9), bg=self.colors['card'], 
                fg=self.colors['fg_secondary']).pack(anchor='w', pady=2)
        
        bg_status = "🟢 Running" if self.uploader.is_background_running() else "🔴 Stopped"
        tk.Label(info_content, text=f"⚡ Background: {bg_status}", 
                font=('Segoe UI', 9, 'bold'), bg=self.colors['card'], 
                fg=self.colors['success'] if self.uploader.is_background_running() else self.colors['danger']).pack(anchor='w', pady=2)
        
        # Main content with 2 columns
        content = tk.Frame(self.root, bg=self.colors['bg'])
        content.pack(fill='both', expand=True, padx=20, pady=10)
        
        left = tk.Frame(content, bg=self.colors['bg'])
        left.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right = tk.Frame(content, bg=self.colors['bg'])
        right.pack(side='left', fill='both', expand=True, padx=(10, 0))
        
        # Left column - Quick Actions
        self.create_card(left, "⚡ Quick Actions", [
            ("🚀 Upload to GitHub", self.upload_code, 'success'),
            ("📊 Git Status", self.show_git_status, 'accent'),
            ("📝 Create .gitignore", self.create_gitignore, 'accent'),
        ])
        
        # Left column - Configuration
        self.create_card(left, "⚙️ Configuration", [
            ("💾 Manage Profiles", self.manage_profiles, 'accent'),
            ("⏰ Auto Upload Settings", self.configure_auto, 'warning'),
            ("📋 Commit Mode", self.configure_commit_mode, 'warning'),
        ])
        
        # Right column - Background
        self.create_card(right, "🔄 Background Mode", [
            ("▶️ Start Background", self.start_background, 'success'),
            ("⏸️ Stop Background", self.stop_background, 'danger'),
            ("📡 View Status", self.show_bg_status, 'accent'),
        ])
        
        # Right column - Utilities
        self.create_card(right, "🛠️ Utilities", [
            ("📄 View Logs", self.view_logs, 'accent'),
            ("🚪 Exit", self.quit_application, 'danger'),
        ])

    def create_card(self, parent, title, buttons):
        """Create a card with buttons"""
        card = tk.Frame(parent, bg=self.colors['card'])
        card.pack(fill='both', expand=True, pady=(0, 15))
        
        tk.Label(card, text=title, font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w', padx=15, pady=(15, 10))
        
        for text, command, color_key in buttons:
            btn = tk.Button(card, text=text, command=command,
                           bg=self.colors[color_key], fg='white',
                           font=('Segoe UI', 10, 'bold'), relief='flat',
                           cursor='hand2', padx=20, pady=10)
            btn.pack(fill='x', padx=15, pady=5)

    def open_advanced_settings(self):
        """Open advanced settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⚙️ Advanced Settings")
        dialog.geometry("650x550")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['bg'])
        
        # Center
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (650 // 2)
        y = (dialog.winfo_screenheight() // 2) - (550 // 2)
        dialog.geometry(f"650x550+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg=self.colors['accent'])
        header.pack(fill='x')
        tk.Label(header, text="⚙️ Advanced Settings", 
                font=('Segoe UI', 16, 'bold'), bg=self.colors['accent'], 
                fg='white').pack(pady=15)
        
        # Notebook for tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Tab 1: Appearance
        appearance_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(appearance_tab, text="🎨 Appearance")
        
        appearance_card = tk.Frame(appearance_tab, bg=self.colors['card'])
        appearance_card.pack(fill='both', expand=True, padx=10, pady=10)
        
        content = tk.Frame(appearance_card, bg=self.colors['card'])
        content.pack(padx=20, pady=20, fill='both', expand=True)
        
        tk.Label(content, text="Choose Theme:", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w', pady=(10, 10))
        
        theme_var = tk.StringVar(value=self.uploader.theme_name)
        
        for theme_name in THEMES.keys():
            rb = tk.Radiobutton(content, text=f"🎨 {theme_name}", 
                               variable=theme_var, value=theme_name,
                               font=('Segoe UI', 10), bg=self.colors['card'], 
                               fg=self.colors['fg'], selectcolor=self.colors['accent'],
                               activebackground=self.colors['card'])
            rb.pack(anchor='w', padx=20, pady=3)
        
        tk.Label(content, text="", bg=self.colors['card']).pack(pady=5)
        
        def apply_theme():
            self.uploader.theme_name = theme_var.get()
            self.uploader.custom_theme = None
            self.uploader.save_settings()
            self.apply_theme()
            self.create_widgets()
            messagebox.showinfo("✅ Success", "Theme applied!", parent=dialog)
        
        tk.Button(content, text="🎨 Apply Theme", command=apply_theme,
                 bg=self.colors['accent'], fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', cursor='hand2', padx=20, pady=10).pack(pady=10)
        
        # Tab 2: Behavior
        behavior_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(behavior_tab, text="⚡ Behavior")
        
        behavior_card = tk.Frame(behavior_tab, bg=self.colors['card'])
        behavior_card.pack(fill='both', expand=True, padx=10, pady=10)
        
        bhv_content = tk.Frame(behavior_card, bg=self.colors['card'])
        bhv_content.pack(padx=20, pady=20, fill='both', expand=True)
        
        tk.Label(bhv_content, text="Window Behavior:", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w', pady=(10, 10))
        
        minimize_var = tk.BooleanVar(value=self.uploader.minimize_to_tray)
        tk.Checkbutton(bhv_content, text="📥 Minimize to system tray when closing", 
                      variable=minimize_var, font=('Segoe UI', 10),
                      bg=self.colors['card'], fg=self.colors['fg'],
                      selectcolor=self.colors['accent'], activebackground=self.colors['card']).pack(anchor='w', padx=20, pady=5)
        
        start_min_var = tk.BooleanVar(value=self.uploader.start_minimized)
        tk.Checkbutton(bhv_content, text="🚀 Start minimized to tray", 
                      variable=start_min_var, font=('Segoe UI', 10),
                      bg=self.colors['card'], fg=self.colors['fg'],
                      selectcolor=self.colors['accent'], activebackground=self.colors['card']).pack(anchor='w', padx=20, pady=5)
        
        tk.Label(bhv_content, text="", bg=self.colors['card']).pack(pady=5)
        
        tk.Label(bhv_content, text="Notifications:", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w', pady=(10, 10))
        
        notif_var = tk.BooleanVar(value=self.uploader.show_notifications)
        tk.Checkbutton(bhv_content, text="🔔 Show upload notifications", 
                      variable=notif_var, font=('Segoe UI', 10),
                      bg=self.colors['card'], fg=self.colors['fg'],
                      selectcolor=self.colors['accent'], activebackground=self.colors['card']).pack(anchor='w', padx=20, pady=5)
        
        sound_var = tk.BooleanVar(value=self.uploader.play_sound)
        tk.Checkbutton(bhv_content, text="🔊 Play sound on completion", 
                      variable=sound_var, font=('Segoe UI', 10),
                      bg=self.colors['card'], fg=self.colors['fg'],
                      selectcolor=self.colors['accent'], activebackground=self.colors['card']).pack(anchor='w', padx=20, pady=5)
        
        def save_behavior():
            self.uploader.minimize_to_tray = minimize_var.get()
            self.uploader.start_minimized = start_min_var.get()
            self.uploader.show_notifications = notif_var.get()
            self.uploader.play_sound = sound_var.get()
            self.uploader.save_settings()
            messagebox.showinfo("✅ Success", "Settings saved!", parent=dialog)
        
        tk.Button(bhv_content, text="💾 Save Settings", command=save_behavior,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', cursor='hand2', padx=20, pady=10).pack(pady=15)
        
        # Tab 3: About
        about_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(about_tab, text="ℹ️ About")
        
        about_card = tk.Frame(about_tab, bg=self.colors['card'])
        about_card.pack(fill='both', expand=True, padx=10, pady=10)
        
        about_content = tk.Frame(about_card, bg=self.colors['card'])
        about_content.pack(padx=20, pady=20, fill='both', expand=True)
        
        tk.Label(about_content, text="🚀 GitHub Auto Upload Tool Pro", 
                font=('Segoe UI', 14, 'bold'), bg=self.colors['card'], 
                fg=self.colors['fg']).pack(pady=(20, 5))
        
        tk.Label(about_content, text="Version 4.0", 
                font=('Segoe UI', 10), bg=self.colors['card'], 
                fg=self.colors['fg_secondary']).pack(pady=2)
        
        tk.Label(about_content, text="", bg=self.colors['card']).pack(pady=10)
        
        features = [
            "✅ Auto upload to GitHub",
            "✅ Multiple profiles support",
            "✅ Background monitoring",
            "✅ Customizable themes",
            "✅ Smart commit modes",
            "✅ System tray integration",
            "✅ Security and encryption",
            "✅ Notifications on events"
        ]
        
        for feature in features:
            tk.Label(about_content, text=feature, font=('Segoe UI', 9),
                    bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w', padx=30, pady=2)
        
        tk.Label(about_content, text="", bg=self.colors['card']).pack(pady=10)
        
        tk.Label(about_content, text="© 2024 GitHub Auto Upload Tool", 
                font=('Segoe UI', 8, 'italic'), bg=self.colors['card'], 
                fg=self.colors['fg_tertiary']).pack(pady=5)
        
        # Close button
        tk.Button(dialog, text="Close", command=dialog.destroy,
                 bg=self.colors['accent'], fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', cursor='hand2', padx=30, pady=10).pack(pady=15)

    def refresh_ui(self):
        """Refresh UI"""
        self.apply_theme()
        self.create_widgets()

    def upload_code(self):
        """Upload code to GitHub"""
        if not self.uploader.repo_path:
            messagebox.showwarning("Warning", "Please configure repository first!")
            return
        
        message = simpledialog.askstring("Commit Message", 
            "Enter commit message (leave empty for auto):", parent=self.root)
        
        if message is None:
            return
        
        progress = tk.Toplevel(self.root)
        progress.title("Uploading...")
        progress.geometry("400x150")
        progress.transient(self.root)
        progress.grab_set()
        progress.protocol("WM_DELETE_WINDOW", lambda: None)
        progress.configure(bg=self.colors['bg'])
        
        tk.Label(progress, text="Uploading to GitHub...", 
                font=('Segoe UI', 12, 'bold'), bg=self.colors['bg'],
                fg=self.colors['fg']).pack(pady=20)
        
        pb = ttk.Progressbar(progress, mode='indeterminate', length=300)
        pb.pack(pady=10)
        pb.start()
        
        status_label = tk.Label(progress, text="Preparing...", font=('Segoe UI', 9),
                               bg=self.colors['bg'], fg=self.colors['fg_secondary'])
        status_label.pack(pady=10)
        
        def update_status(text):
            if progress.winfo_exists():
                status_label.config(text=text)
                progress.update()
        
        def do_upload():
            try:
                self.root.after(0, lambda: update_status("Adding files..."))
                time.sleep(0.5)
                
                if not self.uploader.git_add_all():
                    raise Exception("Git add failed")
                
                self.root.after(0, lambda: update_status("Committing..."))
                time.sleep(0.5)
                
                if not self.uploader.git_commit(message):
                    raise Exception("Commit failed - Nothing to commit")
                
                self.root.after(0, lambda: update_status("Pushing..."))
                time.sleep(0.5)
                
                if not self.uploader.git_push():
                    raise Exception("Push failed")
                
                progress.destroy()
                if self.uploader.show_notifications:
                    messagebox.showinfo("✅ Success", "Uploaded to GitHub!")
            except Exception as e:
                progress.destroy()
                messagebox.showerror("❌ Error", f"Upload failed:\n{str(e)}")
        
        Thread(target=do_upload, daemon=True).start()

    def show_git_status(self):
        """Show git status"""
        self.uploader.show_git_status()

    def create_gitignore(self):
        """Create .gitignore"""
        self.uploader.create_gitignore()

    def manage_profiles(self):
        """Manage profiles"""
        messagebox.showinfo("Info", "Profile manager - Coming soon!")

    def configure_auto(self):
        """Configure auto upload"""
        messagebox.showinfo("Info", "Auto upload settings - Coming soon!")

    def configure_commit_mode(self):
        """Configure commit mode"""
        messagebox.showinfo("Info", "Commit mode settings - Coming soon!")

    def start_background(self):
        """Start background"""
        if self.uploader.start_background_mode():
            if self.uploader.show_notifications:
                messagebox.showinfo("✅ Success", "Background mode started!")
            self.refresh_ui()
        else:
            messagebox.showwarning("⚠️ Warning", "Already running!")

    def stop_background(self):
        """Stop background"""
        if self.uploader.stop_background_mode():
            if self.uploader.show_notifications:
                messagebox.showinfo("✅ Success", "Background mode stopped!")
            self.refresh_ui()

    def show_bg_status(self):
        """Show background status"""
        status = self.uploader.read_status()
        if status:
            msg = f"Time: {status['timestamp']}\nResult: {status['result']}\nMessage: {status['message']}"
            messagebox.showinfo("Status", msg)
        else:
            messagebox.showinfo("Status", "No status available")

    def view_logs(self):
        """View logs"""
        self.uploader.view_logs()

    def quit_application(self):
        """Quit app"""
        if messagebox.askyesno("Exit", "Are you sure?"):
            self.uploader.stop_background_mode()
            if self.tray_manager.icon:
                self.tray_manager.icon.stop()
            self.root.quit()
            sys.exit(0)

    def on_closing(self):
        """Handle closing"""
        if self.uploader.minimize_to_tray:
            self.tray_manager.hide_window()
            if self.uploader.show_notifications:
                messagebox.showinfo("ℹ️ Info", 
                    "App minimized to system tray.\nRight-click tray icon to access menu.")
        else:
            self.quit_application()

    def run(self):
        """Run app"""
        self.root.mainloop()


if __name__ == "__main__":
    app = GitHubUploaderGUI()
    app.run()
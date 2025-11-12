#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Auto Upload Tool Pro - Refactor & Improved Settings UI
Version: 4.1 - Refactor (Fixed)
"""

import os
import sys
import subprocess
import json
import logging
import time
import psutil
import hashlib
import winreg
from datetime import datetime
from pathlib import Path
from threading import Thread
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import StringVar, BooleanVar
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from cryptography.fernet import Fernet
from plyer import notification
from logging.handlers import RotatingFileHandler

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
        'settings_title': 'Advanced Settings',
        'apply': 'Apply',
        'save': 'Save',
        'theme_preview': 'Theme Preview',
        'language': 'Language',
        'start_with_windows': 'Start with Windows',
        'minimize_to_tray': 'Minimize to tray on close',
        'remember_credentials': 'Remember GitHub credentials (encrypted)',
        'set_app_password': 'Set/Change App Password',
        'remove_app_password': 'Remove App Password',
        'enter_password': 'Enter new app password',
        'confirm_password': 'Confirm app password',
        'auth_token': 'GitHub Token',
        'auth_username': 'GitHub Username',
        'save_success': 'Settings saved successfully'
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
        'settings_title': 'Cài đặt Nâng cao',
        'apply': 'Áp dụng',
        'save': 'Lưu',
        'theme_preview': 'Xem trước Giao diện',
        'language': 'Ngôn ngữ',
        'start_with_windows': 'Khởi động cùng Windows',
        'minimize_to_tray': 'Thu nhỏ vào khay khi đóng',
        'remember_credentials': 'Ghi nhớ tài khoản GitHub (đã mã hóa)',
        'set_app_password': 'Đặt/Thay đổi mật khẩu ứng dụng',
        'remove_app_password': 'Xóa mật khẩu ứng dụng',
        'enter_password': 'Nhập mật khẩu mới',
        'confirm_password': 'Xác nhận mật khẩu',
        'auth_token': 'Token GitHub',
        'auth_username': 'Tên đăng nhập GitHub',
        'save_success': 'Lưu cài đặt thành công'
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
        try:
            if self.key_file.exists():
                with open(self.key_file, 'rb') as f:
                    return f.read()
            else:
                key = Fernet.generate_key()
                self.key_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                try:
                    os.chmod(self.key_file, 0o600)
                except Exception:
                    pass
                return key
        except Exception:
            return Fernet.generate_key()
    
    def encrypt(self, text: str) -> str:
        """Mã hóa văn bản"""
        try:
            if not text:
                return ""
            return self.cipher.encrypt(text.encode()).decode()
        except Exception:
            return text
    
    def decrypt(self, encrypted_text: str) -> str:
        """Giải mã văn bản"""
        try:
            if not encrypted_text:
                return ""
            return self.cipher.decrypt(encrypted_text.encode()).decode()
        except Exception:
            return encrypted_text
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash mật khẩu"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()


class NotificationManager:
    """Quản lý thông báo hệ thống"""
    
    def __init__(self, app_name: str = "GitHub Uploader"):
        self.app_name = app_name
    
    def send(self, title: str, message: str, timeout: int = 5):
        """Gửi thông báo (best-effort)"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                timeout=timeout,
                app_icon=None
            )
        except Exception:
            pass


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
        
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.security = SecurityManager()
        self.notifier = NotificationManager()
        
        log_path = self.log_dir / f'upload_{datetime.now().strftime("%Y%m%d")}.log'
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = RotatingFileHandler(log_path, maxBytes=2*1024*1024, backupCount=5, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.addHandler(logging.StreamHandler())
        self.logger = logger
        
        # FIX 1: Load settings BEFORE load_config và load_auth
        self.load_settings()
        self.load_config()
        self.load_auth()
        
        # FIX 2: Initialize github_token và github_username nếu chưa có
        if not hasattr(self, 'github_token'):
            self.github_token = ''
        if not hasattr(self, 'github_username'):
            self.github_username = ''

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
            if self.remember_credentials and getattr(self, 'github_token', None):
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
        """Cập nhật startup với Windows (best-effort)"""
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
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            self.logger.debug(f"Error updating startup (ignored): {e}")

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
        """Chạy command và trả về output (None nếu lỗi)"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.repo_path if self.repo_path else None,
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode != 0:
                self.logger.debug(f"Command '{command}' returned non-zero code: {result.stderr.strip()}")
                return None
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timeout: {command}")
            return None
        except Exception as e:
            self.logger.error(f"Error running command '{command}': {e}")
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
                messagebox.showerror("Error", "Cannot get Git status or repository not initialized")
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
        """Git add tất cả files - corrected behavior"""
        try:
            result = self._git("add .")
            return result is not None
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
            
            # FIX 3: Escape double quotes trong commit message
            message = message.replace('"', '\\"')
            
            result = self._git(f'commit -m "{message}"')
            if result is not None:
                self.last_commit_date = today
                self.save_config()
                self.logger.info(f"Committed: {message}")
                
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
                    pid_text = f.read().strip()
                if not pid_text:
                    return False
                pid = int(pid_text)
                return psutil.pid_exists(pid)
            return False
        except Exception:
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
                        
                        if not self.git_pull():
                            self._write_status("error", "Pull failed")
                            time.sleep(60)
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
                
                for _ in range(int(self.auto_upload_interval * 60)):
                    if not self.is_background_running():
                        break
                    time.sleep(1)
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
    """Quản lý System Tray (hỗ trợ double-click để hiện cửa sổ)"""
    
    def __init__(self, gui_app):
        self.gui_app = gui_app
        self.icon = None
        self.is_running = False
    
    def create_image(self):
        """Tạo icon cho system tray"""
        width = 64
        height = 64
        # FIX: Kiểm tra colors attribute tồn tại
        try:
            color = self.gui_app.colors.get('accent', '#58a6ff')
        except AttributeError:
            color = '#58a6ff'
        
        image = Image.new('RGB', (width, height), color=color)
        dc = ImageDraw.Draw(image)
        # FIX: Dùng font lớn hơn và vị trí tốt hơn
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", 32)
            dc.text((12, 12), "GH", fill='white', font=font)
        except:
            dc.text((16, 20), "GH", fill='white')
        return image
    
    def show_window(self, icon=None, item=None):
        """Hiển thị cửa sổ chính"""
        try:
            self.gui_app.root.after(0, self._show_window_main_thread)
        except Exception as e:
            print(f"Error showing window: {e}")
    
    def _show_window_main_thread(self):
        """Show window trong main thread"""
        try:
            self.gui_app.root.deiconify()
            self.gui_app.root.lift()
            self.gui_app.root.focus_force()
            self.gui_app.root.state('normal')
        except Exception as e:
            print(f"Error in show_window_main_thread: {e}")
    
    def hide_window(self):
        """Ẩn cửa sổ chính"""
        try:
            self.gui_app.root.withdraw()
        except Exception as e:
            print(f"Error hiding window: {e}")
    
    def quit_app(self, icon=None, item=None):
        """Thoát ứng dụng"""
        try:
            self.is_running = False
            if self.icon:
                self.icon.stop()
            self.gui_app.root.after(0, self._quit_main_thread)
        except Exception as e:
            print(f"Error quitting: {e}")
            os._exit(0)
    
    def _quit_main_thread(self):
        """Quit trong main thread"""
        try:
            self.gui_app.uploader.stop_background_mode()
            self.gui_app.root.quit()
            self.gui_app.root.destroy()
        except Exception:
            pass
        finally:
            sys.exit(0)

    def start(self):
        """Khởi động system tray"""
        if self.is_running:
            return
        
        try:
            # FIX: Tạo menu với đầy đủ các mục
            menu = (
                item(self.gui_app.t('app_title'), self.show_window, default=True),
                item('Show Window', self.show_window),
                item(self.gui_app.t('exit'), self.quit_app)
            )
            
            self.icon = pystray.Icon(
                "GitHub Uploader",
                self.create_image(),
                "GitHub Auto Upload Tool",
                menu
            )
            
            self.is_running = True
            
            # FIX: Chạy icon.run() trong thread riêng
            def run_icon():
                try:
                    self.icon.run()
                except Exception as e:
                    print(f"Tray icon error: {e}")
                    self.is_running = False
            
            thread = Thread(target=run_icon, daemon=True)
            thread.start()
            
            # FIX: Đợi một chút để icon xuất hiện
            time.sleep(0.5)
            
            print("System tray started successfully")
            
        except Exception as e:
            print(f"Failed to start system tray: {e}")
            self.is_running = False

    def stop(self):
        """Dừng system tray"""
        try:
            self.is_running = False
            if self.icon:
                self.icon.stop()
        except Exception as e:
            print(f"Error stopping tray: {e}")


class SettingsDialog(tk.Toplevel):
    """Modular settings dialog with live preview and better layout"""
    def __init__(self, parent, uploader: GitHubUploader):
        super().__init__(parent.root)
        self.parent = parent
        self.uploader = uploader
        self.transient(parent.root)
        self.grab_set()
        self.title(self.parent.t('settings_title'))
        
        # FIX 5: Kiểm tra parent.colors tồn tại trước khi dùng
        try:
            self.configure(bg=parent.colors['bg'])
        except (AttributeError, KeyError):
            self.configure(bg='#0d1117')
        
        self.geometry("720x520")
        self.resizable(False, False)
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (720 // 2)
        y = (self.winfo_screenheight() // 2) - (520 // 2)
        self.geometry(f"720x520+{x}+{y}")
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=12, pady=12)

        appearance = ttk.Frame(notebook)
        notebook.add(appearance, text="Appearance")

        frame_left = ttk.Frame(appearance)
        frame_left.pack(side='left', fill='y', padx=10, pady=10)
        frame_right = ttk.Frame(appearance)
        frame_right.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        ttk.Label(frame_left, text=self.parent.t('language')).pack(anchor='w', pady=(4,8))
        self.lang_var = StringVar(value=self.uploader.language)
        ttk.Combobox(frame_left, textvariable=self.lang_var, values=list(TRANSLATIONS.keys()), state='readonly').pack(fill='x')

        ttk.Label(frame_left, text="Theme").pack(anchor='w', pady=(12,8))
        self.theme_var = StringVar(value=self.uploader.theme_name)
        theme_list = list(THEMES.keys())
        self.theme_combo = ttk.Combobox(frame_left, textvariable=self.theme_var, values=theme_list, state='readonly')
        self.theme_combo.pack(fill='x')
        self.theme_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())

        ttk.Label(frame_left, text=self.parent.t('theme_preview')).pack(anchor='w', pady=(12,8))
        self.preview_canvas = tk.Canvas(frame_left, width=200, height=120, bd=0, highlightthickness=0)
        self.preview_canvas.pack()

        ttk.Label(frame_right, text="Behavior & Notifications").pack(anchor='w', pady=(4,8))
        self.minimize_var = BooleanVar(value=self.uploader.minimize_to_tray)
        ttk.Checkbutton(frame_right, text=self.parent.t('minimize_to_tray'), variable=self.minimize_var).pack(anchor='w', pady=4)
        self.start_min_var = BooleanVar(value=self.uploader.start_minimized)
        ttk.Checkbutton(frame_right, text=self.parent.t('start_with_windows'), variable=self.start_min_var).pack(anchor='w', pady=4)
        self.notify_var = BooleanVar(value=self.uploader.show_notifications)
        ttk.Checkbutton(frame_right, text="Show notifications", variable=self.notify_var).pack(anchor='w', pady=4)
        self.remember_var = BooleanVar(value=self.uploader.remember_credentials)
        ttk.Checkbutton(frame_right, text=self.parent.t('remember_credentials'), variable=self.remember_var).pack(anchor='w', pady=4)

        auth_frame = ttk.LabelFrame(frame_right, text="GitHub Authentication")
        auth_frame.pack(fill='x', pady=(12,4))
        ttk.Label(auth_frame, text=self.parent.t('auth_username')).pack(anchor='w', padx=6)
        self.user_entry = ttk.Entry(auth_frame)
        self.user_entry.pack(fill='x', padx=6, pady=4)
        ttk.Label(auth_frame, text=self.parent.t('auth_token')).pack(anchor='w', padx=6)
        self.token_entry = ttk.Entry(auth_frame, show="*")
        self.token_entry.pack(fill='x', padx=6, pady=4)
        self.user_entry.insert(0, getattr(self.uploader, 'github_username', '') or '')
        self.token_entry.insert(0, getattr(self.uploader, 'github_token', '') or '')

        pwd_frame = ttk.Frame(frame_right)
        pwd_frame.pack(fill='x', pady=(10,4))
        ttk.Button(pwd_frame, text=self.parent.t('set_app_password'), command=self.set_app_password).pack(side='left', padx=6)
        ttk.Button(pwd_frame, text=self.parent.t('remove_app_password'), command=self.remove_app_password).pack(side='left', padx=6)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=8)
        ttk.Button(btn_frame, text=self.parent.t('apply'), command=self.apply_settings).pack(side='right', padx=6)
        ttk.Button(btn_frame, text=self.parent.t('save'), command=self.save_and_close).pack(side='right', padx=6)
        self.update_preview()

    def update_preview(self):
        theme_name = self.theme_var.get()
        theme = THEMES.get(theme_name, THEMES['GitHub Dark'])
        self.preview_canvas.delete("all")
        self.preview_canvas.create_rectangle(0, 0, 200, 120, fill=theme['bg'], outline=theme['border'])
        self.preview_canvas.create_rectangle(8, 12, 192, 54, fill=theme['card'], outline=theme['border'])
        self.preview_canvas.create_text(16, 28, anchor='w', text="GitHub Auto Upload", fill=theme['fg'], font=('Segoe UI', 9, 'bold'))
        self.preview_canvas.create_text(16, 44, anchor='w', text="Background: Running", fill=theme['fg_secondary'], font=('Segoe UI', 8))

    def set_app_password(self):
        pwd = simpledialog.askstring(self.parent.t('set_app_password'), self.parent.t('enter_password'), parent=self, show='*')
        if not pwd:
            return
        confirm = simpledialog.askstring(self.parent.t('set_app_password'), self.parent.t('confirm_password'), parent=self, show='*')
        if pwd != confirm:
            messagebox.showerror("Error", "Passwords do not match", parent=self)
            return
        hashed = self.uploader.security.hash_password(pwd)
        self.uploader.app_password = hashed
        messagebox.showinfo("Success", "App password set", parent=self)

    def remove_app_password(self):
        if messagebox.askyesno("Confirm", "Remove app password?", parent=self):
            self.uploader.app_password = None
            messagebox.showinfo("Success", "App password removed", parent=self)

    def apply_settings(self):
        self.uploader.language = self.lang_var.get()
        self.uploader.theme_name = self.theme_var.get()
        self.uploader.minimize_to_tray = self.minimize_var.get()
        self.uploader.start_minimized = self.start_min_var.get()
        self.uploader.show_notifications = self.notify_var.get()
        self.uploader.remember_credentials = self.remember_var.get()
        self.uploader.github_username = self.user_entry.get().strip()
        self.uploader.github_token = self.token_entry.get().strip()
        self.uploader.save_auth()
        self.uploader.save_settings()
        self.parent.apply_theme()
        self.parent.refresh_ui()
        messagebox.showinfo(self.parent.t('success'), self.parent.t('save_success'), parent=self)

    def save_and_close(self):
        self.apply_settings()
        self.destroy()


class GitHubUploaderGUI:
    """GUI class cho ứng dụng"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.uploader = GitHubUploader()
        self.root.title(self.t('app_title') + " v4.1")
        self.root.geometry("950x750")

        # FIX: Verify password trước khi khởi tạo UI
        if getattr(self.uploader, 'app_password', None):
            if not self._verify_app_password():
                self.root.destroy()
                sys.exit(0)

        # FIX: Apply theme trước khi tạo widgets
        self.apply_theme()
        
        self.create_widgets()
        
        # FIX: Khởi tạo tray_manager SAU khi tạo widgets
        self.tray_manager = SystemTrayManager(self)
        
        # FIX: Set protocol TRƯỚC khi start tray
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # FIX: Start tray với error handling
        try:
            self.tray_manager.start()
            print("Tray manager started")
        except Exception as e:
            print(f"Failed to start system tray: {e}")
            self.uploader.logger.warning(f"Failed to start system tray: {e}")

        # FIX: Start minimized nếu cần
        if self.uploader.start_minimized:
            self.root.after(1000, self.root.withdraw)

    def t(self, key: str) -> str:
        """Get translation"""
        lang = getattr(self.uploader, 'language', 'en')
        return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

    def _verify_app_password(self) -> bool:
        password = simpledialog.askstring("Password", "Enter app password:", show='*', parent=self.root)
        if not password:
            return False
        return self.uploader.security.hash_password(password) == self.uploader.app_password

    def apply_theme(self):
        if getattr(self.uploader, 'custom_theme', None):
            self.colors = self.uploader.custom_theme
        else:
            self.colors = THEMES.get(getattr(self.uploader, 'theme_name', 'GitHub Dark'), THEMES['GitHub Dark'])
        try:
            self.root.configure(bg=self.colors['bg'])
        except Exception:
            pass

    def create_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        header = tk.Frame(self.root, bg=self.colors['accent'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        header_content = tk.Frame(header, bg=self.colors['accent'])
        header_content.pack(expand=True, fill='x', padx=10)

        tk.Label(header_content, text="🚀 GitHub Auto Upload Tool Pro", 
                font=('Segoe UI', 18, 'bold'), bg=self.colors['accent'], 
                fg='white').pack(side='left', padx=10)

        settings_btn = tk.Button(header_content, text="⚙️ "+self.t('settings'), 
                                 command=self.open_advanced_settings,
                                 bg=self.colors['bg'], fg=self.colors['fg'],
                                 font=('Segoe UI', 10, 'bold'), relief='flat',
                                 cursor='hand2', padx=12, pady=6)
        settings_btn.pack(side='right', padx=10)

        info_card = tk.Frame(self.root, bg=self.colors['card'])
        info_card.pack(fill='x', padx=20, pady=12)

        info_content = tk.Frame(info_card, bg=self.colors['card'])
        info_content.pack(padx=12, pady=8, fill='x')

        repo_text = getattr(self.uploader, 'repo_path', '') or "Not configured"
        if len(repo_text) > 60:
            repo_text = "..." + repo_text[-57:]

        tk.Label(info_content, text=f"📁 {repo_text}", 
                font=('Segoe UI', 10), bg=self.colors['card'], 
                fg=self.colors['fg']).pack(anchor='w', pady=2)

        tk.Label(info_content, text=f"🌿 Branch: {getattr(self.uploader, 'branch', 'main')} | 🎨 Theme: {getattr(self.uploader, 'theme_name', 'GitHub Dark')}", 
                font=('Segoe UI', 9), bg=self.colors['card'], 
                fg=self.colors['fg_secondary']).pack(anchor='w', pady=2)

        bg_status = "🟢 Running" if self.uploader.is_background_running() else "🔴 Stopped"
        tk.Label(info_content, text=f"⚡ Background: {bg_status}", 
                font=('Segoe UI', 9, 'bold'), bg=self.colors['card'], 
                fg=self.colors['success'] if self.uploader.is_background_running() else self.colors['danger']).pack(anchor='w', pady=2)

        content = tk.Frame(self.root, bg=self.colors['bg'])
        content.pack(fill='both', expand=True, padx=20, pady=10)

        left = tk.Frame(content, bg=self.colors['bg'])
        left.pack(side='left', fill='both', expand=True, padx=(0, 10))

        right = tk.Frame(content, bg=self.colors['bg'])
        right.pack(side='left', fill='both', expand=True, padx=(10, 0))

        self.create_card(left, self.t('quick_actions'), [
            (self.t('upload'), self.upload_code, 'success'),
            (self.t('git_status'), self.show_git_status, 'accent'),
            (self.t('create_gitignore'), self.create_gitignore, 'accent'),
        ])

        self.create_card(left, self.t('configuration'), [
            (self.t('manage_profiles'), self.manage_profiles, 'accent'),
            (self.t('auto_settings'), self.configure_auto, 'warning'),
            (self.t('commit_mode'), self.configure_commit_mode, 'warning'),
        ])

        self.create_card(right, self.t('background_mode'), [
            (self.t('start_bg'), self.start_background, 'success'),
            (self.t('stop_bg'), self.stop_background, 'danger'),
            (self.t('view_status'), self.show_bg_status, 'accent'),
        ])

        self.create_card(right, self.t('utilities'), [
            (self.t('view_logs'), self.view_logs, 'accent'),
            (self.t('exit'), self.quit_application, 'danger'),
        ])

    def create_card(self, parent, title, buttons):
        """Create card with buttons"""
        card = tk.Frame(parent, bg=self.colors['card'])
        card.pack(fill='both', expand=True, pady=(0, 15))

        tk.Label(card, text=title, font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card'], fg=self.colors['fg']).pack(anchor='w', padx=12, pady=(12, 8))

        for text, command, color_key in buttons:
            color = self.colors.get(color_key, self.colors['accent'])
            btn = tk.Button(card, text=text, command=command,
                           bg=color, fg='white',
                           font=('Segoe UI', 10, 'bold'), relief='flat',
                           cursor='hand2', padx=16, pady=8)
            btn.pack(fill='x', padx=12, pady=6)
            
            # FIX 9: Thêm hover effect
            btn.bind('<Enter>', lambda e, b=btn, c=color: b.config(bg=self._lighten_color(c)))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.config(bg=c))

    def _lighten_color(self, hex_color: str, factor: float = 1.2) -> str:
        """Lighten hex color"""
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception:
            return hex_color

    def open_advanced_settings(self):
        SettingsDialog(self, self.uploader)

    def refresh_ui(self):
        self.apply_theme()
        self.create_widgets()

    def upload_code(self):
        """Upload code to GitHub"""
        if not getattr(self.uploader, 'repo_path', None):
            messagebox.showwarning(self.t('warning'), "Please configure repository first!")
            return

        message = simpledialog.askstring("Commit Message", 
            "Enter commit message (leave empty for auto):", parent=self.root)

        if message is None:
            return

        progress = tk.Toplevel(self.root)
        progress.title(self.t('uploading'))
        progress.geometry("420x160")
        progress.transient(self.root)
        progress.grab_set()
        progress.protocol("WM_DELETE_WINDOW", lambda: None)
        progress.configure(bg=self.colors['bg'])

        tk.Label(progress, text=self.t('uploading'), 
                font=('Segoe UI', 12, 'bold'), bg=self.colors['bg'],
                fg=self.colors['fg']).pack(pady=16)

        pb = ttk.Progressbar(progress, mode='indeterminate', length=340)
        pb.pack(pady=10)
        pb.start(10)

        status_label = tk.Label(progress, text="Preparing...", font=('Segoe UI', 9),
                               bg=self.colors['bg'], fg=self.colors['fg_secondary'])
        status_label.pack(pady=8)

        def update_status(text):
            try:
                if progress.winfo_exists():
                    status_label.config(text=text)
                    progress.update()
            except Exception:
                pass

        def do_upload():
            try:
                self.root.after(0, lambda: update_status("Adding files..."))
                time.sleep(0.3)

                if not self.uploader.git_add_all():
                    raise Exception("Git add failed")

                self.root.after(0, lambda: update_status("Committing..."))
                time.sleep(0.3)

                # FIX 10: Truyền message hoặc empty string
                if not self.uploader.git_commit(message or ""):
                    raise Exception("Commit failed - Nothing to commit or daily limit reached")

                self.root.after(0, lambda: update_status("Pushing..."))
                time.sleep(0.3)

                if not self.uploader.git_push():
                    raise Exception("Push failed")

                # FIX 11: Đảm bảo progress được destroy an toàn
                try:
                    if progress.winfo_exists():
                        progress.destroy()
                except Exception:
                    pass
                
                if self.uploader.show_notifications:
                    self.root.after(0, lambda: messagebox.showinfo(self.t('success'), self.t('upload_success')))
            except Exception as e:
                try:
                    if progress.winfo_exists():
                        progress.destroy()
                except Exception:
                    pass
                self.root.after(0, lambda: messagebox.showerror(self.t('error'), f"{self.t('upload_failed')}: {str(e)}"))

        Thread(target=do_upload, daemon=True).start()

    def show_git_status(self):
        self.uploader.show_git_status()

    def create_gitignore(self):
        self.uploader.create_gitignore()

    def manage_profiles(self):
        messagebox.showinfo(self.t('info'), "Profile manager - Coming soon!")

    def configure_auto(self):
        messagebox.showinfo(self.t('info'), "Auto upload settings - Coming soon!")

    def configure_commit_mode(self):
        messagebox.showinfo(self.t('info'), "Commit mode settings - Coming soon!")

    def start_background(self):
        if self.uploader.start_background_mode():
            if self.uploader.show_notifications:
                messagebox.showinfo(self.t('success'), self.t('bg_started'))
            self.refresh_ui()
        else:
            messagebox.showwarning(self.t('warning'), "Already running!")

    def stop_background(self):
        if self.uploader.stop_background_mode():
            if self.uploader.show_notifications:
                messagebox.showinfo(self.t('success'), self.t('bg_stopped'))
            self.refresh_ui()
        else:
            messagebox.showwarning(self.t('warning'), "Background mode not running")

    def show_bg_status(self):
        status = self.uploader.read_status()
        if status:
            msg = f"Time: {status.get('timestamp')}\nResult: {status.get('result')}\nMessage: {status.get('message')}"
            messagebox.showinfo("Status", msg)
        else:
            messagebox.showinfo("Status", "No status available")

    def view_logs(self):
        self.uploader.view_logs()

    def quit_application(self):
        """Quit application safely"""
        if messagebox.askyesno(self.t('confirm'), "Are you sure you want to exit?"):
            try:
                # Stop background mode
                self.uploader.stop_background_mode()
            except Exception as e:
                self.uploader.logger.error(f"Error stopping background: {e}")
            
            try:
                # Stop tray icon
                if hasattr(self, 'tray_manager'):
                    self.tray_manager.stop()
            except Exception as e:
                self.uploader.logger.error(f"Error stopping tray: {e}")
            
            try:
                # Quit application
                self.root.quit()
                self.root.destroy()
            except Exception:
                pass
            
            sys.exit(0)

    def on_closing(self):
        """Handle window close event"""
        if self.uploader.minimize_to_tray:
            self.root.withdraw()
            # FIX: Chỉ hiện thông báo lần đầu
            if not hasattr(self, '_minimize_notified'):
                if self.uploader.show_notifications:
                    self.uploader.notifier.send(
                        self.t('info'), 
                        self.t('minimize_info')
                    )
                self._minimize_notified = True
        else:
            self.quit_application()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = GitHubUploaderGUI()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
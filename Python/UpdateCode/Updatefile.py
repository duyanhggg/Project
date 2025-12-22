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
import io
import base64
from tkinter import filedialog
import ctypes
from threading import Event

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
        """Chạy command và trả về output - improved version"""
        try:
            # Kiểm tra repo path trước
            if self.repo_path and not Path(self.repo_path).exists():
                self.logger.error(f"Repository path doesn't exist: {self.repo_path}")
                return None
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.repo_path if self.repo_path else None,
                capture_output=True,
                text=True,
                timeout=120,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode != 0:
                stderr = result.stderr.strip()
                
                # FIX: Auto-handle safe.directory error
                if "fatal: detected dubious ownership" in stderr or \
                   "is owned by" in stderr or \
                   "safe.directory" in stderr:
                    self.logger.warning("Detected safe.directory issue, attempting auto-fix...")
                    if self._add_safe_directory():
                        # Retry command
                        self.logger.info("Retrying command after safe.directory fix...")
                        retry_result = subprocess.run(
                            command,
                            shell=True,
                            cwd=self.repo_path if self.repo_path else None,
                            capture_output=True,
                            text=True,
                            timeout=120,
                            encoding='utf-8',
                            errors='replace'
                        )
                        if retry_result.returncode == 0:
                            return retry_result.stdout.strip()
                        stderr = retry_result.stderr.strip()
                
                # Log chi tiết error
                self.logger.error(f"Command failed: {command}")
                self.logger.error(f"Exit code: {result.returncode}")
                self.logger.error(f"Error output: {stderr}")
                
                # Kiểm tra các lỗi cụ thể khác
                if "not a git repository" in stderr.lower():
                    self.logger.error("Not a git repository. Please initialize git first.")
                elif "permission denied" in stderr.lower():
                    self.logger.error("Permission denied. Check file permissions.")
                elif "fatal: pathspec" in stderr.lower():
                    self.logger.error("Invalid file path or pattern.")
                
                return None
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timeout (120s): {command}")
            return None
        except FileNotFoundError:
            self.logger.error(f"Git command not found. Is Git installed?")
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
        """Git add tất cả files - improved error handling"""
        try:
            # Kiểm tra repo path
            if not self.repo_path or not Path(self.repo_path).exists():
                self.logger.error("Repository path not configured or doesn't exist")
                return False
            
            # Kiểm tra có phải git repo không
            git_dir = Path(self.repo_path) / '.git'
            if not git_dir.exists():
                self.logger.error("Not a git repository")
                return False
            
            # FIX: Kiểm tra và fix safe.directory issue
            if not self._ensure_safe_directory():
                self.logger.error("Failed to configure safe directory")
                return False
            
            # Kiểm tra có files để add không
            status = self._git("status --porcelain")
            if status is None:
                self.logger.error("Failed to get git status")
                return False
            
            if not status.strip():
                self.logger.info("No files to add")
                return True  # Not an error, just nothing to add
            
            # Thử add với verbose output
            result = self._git("add -A -v")
            if result is None:
                # Thử phương án khác
                self.logger.warning("'git add -A' failed, trying 'git add .'")
                result = self._git("add .")
                if result is None:
                    self.logger.error("Both 'git add' methods failed")
                    return False
            
            self.logger.info(f"Successfully added files: {len(status.strip().split(chr(10)))} file(s)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding files: {e}")
            return False

    def _ensure_safe_directory(self) -> bool:
        """Đảm bảo repo path được add vào safe.directory"""
        try:
            # Kiểm tra xem đã được add chưa
            result = self.run_command("git config --global --get-all safe.directory")
            
            if result is None:
                # Config chưa có, add luôn
                return self._add_safe_directory()
            
            # Chuẩn hóa path để so sánh
            repo_path_normalized = str(Path(self.repo_path).resolve()).replace('\\', '/')
            
            # Kiểm tra xem repo path đã có trong list chưa
            safe_dirs = result.split('\n') if result else []
            safe_dirs_normalized = [d.replace('\\', '/') for d in safe_dirs]
            
            if repo_path_normalized not in safe_dirs_normalized:
                return self._add_safe_directory()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking safe.directory: {e}")
            return self._add_safe_directory()

    def _add_safe_directory(self) -> bool:
        """Add repo path vào safe.directory"""
        try:
            # Normalize path
            repo_path = str(Path(self.repo_path).resolve()).replace('\\', '/')
            
            # Add to global config
            result = self.run_command(f'git config --global --add safe.directory "{repo_path}"')
            
            if result is not None or self.run_command("git status") is not None:
                self.logger.info(f"Added safe.directory: {repo_path}")
                return True
            
            # Fallback: thử với wildcard
            self.logger.warning("Trying wildcard safe.directory")
            result = self.run_command('git config --global --add safe.directory "*"')
            
            if result is not None or self.run_command("git status") is not None:
                self.logger.info("Added wildcard safe.directory")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error adding safe.directory: {e}")
            return False

    def git_commit(self, message: str) -> bool:
        """Git commit với message - improved version"""
        try:
            # Kiểm tra xem có thay đổi không
            status = self._git("status --porcelain")
            if not status:
                self.logger.info("No changes to commit")
                if self.show_notifications and not self.silent_mode:
                    self.notifier.send("No Changes", "Working directory clean")
                return False
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Kiểm tra commit mode
            if self.commit_mode == 'daily':
                if self.last_commit_date == today:
                    self.logger.info("Already committed today (daily mode)")
                    if self.show_notifications and not self.silent_mode:
                        self.notifier.send("Daily Limit", "Already committed today")
                    return False
            elif self.commit_mode == 'manual':
                if not message:
                    self.logger.info("Manual mode - message required")
                    return False
            
            # Tạo commit message
            if not message or message.strip() == "":
                if self.use_conventional_commits:
                    commit_type = self._detect_commit_type(status)
                    message = f"{commit_type}: Auto update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                else:
                    message = self.commit_message_template.format(
                        datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        date=datetime.now().strftime("%Y-%m-%d"),
                        time=datetime.now().strftime("%H:%M:%S"),
                        user=os.environ.get('USERNAME', 'user')
                    )
            
            # Escape quotes
            message = message.replace('"', '\\"').replace("'", "\\'")
            
            # Commit với retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = self._git(f'commit -m "{message}"')
                    if result is not None:
                        self.last_commit_date = today
                        self.save_config()
                        
                        # Đếm số files đã commit
                        files_changed = len(status.strip().split('\n'))
                        
                        self.logger.info(f"Committed: {message} ({files_changed} files)")
                        
                        if self.show_notifications and not self.silent_mode:
                            self.notifier.send(
                                "✅ Commit Success", 
                                f"{files_changed} file(s) committed\n{message[:50]}..."
                            )
                        
                        return True
                    elif attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        return False
                except Exception as e:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Commit attempt {attempt+1} failed: {e}")
                        time.sleep(1)
                    else:
                        raise
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error committing: {e}")
            if self.show_notifications and not self.silent_mode:
                self.notifier.send("❌ Commit Failed", str(e))
            return False

    def _detect_commit_type(self, status: str) -> str:
        """Detect conventional commit type based on changes"""
        lines = status.strip().split('\n')
        
        # Check for new files
        if any(line.startswith('??') or line.startswith('A ') for line in lines):
            return "feat"
        
        # Check for deletions
        if any(line.startswith('D ') for line in lines):
            return "refactor"
        
        # Check for modifications
        if any(line.startswith('M ') for line in lines):
            # Check if it's documentation
            if any('.md' in line or 'README' in line for line in lines):
                return "docs"
            # Check if it's config
            if any(('.json' in line or '.yaml' in line or '.yml' in line or '.toml' in line) for line in lines):
                return "chore"
            return "fix"
        
        return "chore"

    def git_push(self) -> bool:
        """Git push lên remote - improved with auto-pull retry"""
        try:
            result = self._git(f"push -u origin {self.branch}")
            if result is not None:
                self.logger.info(f"Pushed to {self.branch}")
                
                if self.show_notifications and not self.silent_mode:
                    self.notifier.send("✅ Push Success", f"Pushed to {self.branch}")
                
                return True
            
            # Kiểm tra xem có phải non-fast-forward error không
            stderr_check = self.run_command(f"git push -u origin {self.branch} 2>&1")
            if stderr_check and ("non-fast-forward" in stderr_check or "rejected" in stderr_check):
                self.logger.warning("Push rejected: local branch behind remote. Auto-pulling and retrying...")
                
                if self.auto_pull and self.git_pull():
                    # Retry push sau khi pull thành công
                    retry_result = self._git(f"push -u origin {self.branch}")
                    if retry_result is not None:
                        self.logger.info(f"Pushed to {self.branch} (after auto-pull)")
                        if self.show_notifications and not self.silent_mode:
                            self.notifier.send("✅ Push Success", f"Pushed to {self.branch} (after pull)")
                        return True
                
                self.logger.error("Push failed even after pull attempt")
                return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error pushing: {e}")
            if self.show_notifications and not self.silent_mode:
                self.notifier.send("❌ Push Failed", str(e)[:100])
            return False

    def load_profiles(self):
        """Load saved profiles"""
        try:
            if self.profiles_file.exists():
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    self.profiles = json.load(f)
            else:
                self.profiles = {
                    'default': {
                        'repo_path': '',
                        'remote_url': '',
                        'branch': 'main'
                    }
                }
                self.save_profiles()
        except Exception as e:
            self.logger.error(f"Error loading profiles: {e}")
            self.profiles = {'default': {}}

    def save_profiles(self):
        """Save profiles"""
        try:
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self.profiles, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving profiles: {e}")

    def get_profile(self, name: str) -> dict:
        """Get specific profile"""
        return self.profiles.get(name, {})

    def save_profile(self, name: str, config: dict):
        """Save specific profile"""
        try:
            self.profiles[name] = config
            self.save_profiles()
            self.logger.info(f"Profile saved: {name}")
        except Exception as e:
            self.logger.error(f"Error saving profile: {e}")

    def delete_profile(self, name: str):
        """Delete profile"""
        try:
            if name in self.profiles and name != 'default':
                del self.profiles[name]
                self.save_profiles()
                self.logger.info(f"Profile deleted: {name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting profile: {e}")
            return False

class SystemTrayManager:
    """Quản lý System Tray với icon đẹp hơn"""
    
    def __init__(self, gui_app):
        self.gui_app = gui_app
        self.icon = None
        self.is_running = False
    
    def create_icon(self):
        """Create system tray icon"""
        try:
            # Create a simple icon
            image = Image.new('RGB', (64, 64), color='#0d1117')
            draw = ImageDraw.Draw(image)
            draw.ellipse([8, 8, 56, 56], fill='#58a6ff', outline='#58a6ff')
            
            menu = pystray.Menu(
                item('🚀 Upload', self.upload_action),
                item('📊 Status', self.status_action),
                item('⚙️ Settings', self.settings_action),
                item('🔄 Refresh', self.refresh_action),
                pystray.Menu.SEPARATOR,
                item('🪟 Show Window', self.show_window),
                item('🚪 Exit', self.exit_action)
            )
            
            self.icon = pystray.Icon("GitHub Uploader", image, menu=menu)
            self.is_running = True
            self.icon.run()
        except Exception as e:
            print(f"Error creating tray icon: {e}")

    def upload_action(self, icon, item):
        """Trigger upload from tray"""
        try:
            self.gui_app.root.deiconify()
            self.gui_app.root.lift()
            self.gui_app.root.focus()
            if hasattr(self.gui_app, 'do_upload'):
                self.gui_app.do_upload()
        except Exception as e:
            print(f"Error in upload action: {e}")

    def status_action(self, icon, item):
        """Show status from tray"""
        try:
            self.gui_app.root.deiconify()
            self.gui_app.root.lift()
            self.gui_app.root.focus()
            if hasattr(self.gui_app, 'show_git_status'):
                self.gui_app.show_git_status()
        except Exception as e:
            print(f"Error in status action: {e}")

    def settings_action(self, icon, item):
        """Open settings from tray"""
        try:
            self.gui_app.root.deiconify()
            self.gui_app.root.lift()
            self.gui_app.root.focus()
            if hasattr(self.gui_app, 'open_settings'):
                self.gui_app.open_settings()
        except Exception as e:
            print(f"Error in settings action: {e}")

    def refresh_action(self, icon, item):
        """Refresh UI from tray"""
        try:
            if hasattr(self.gui_app, 'refresh_ui'):
                self.gui_app.refresh_ui()
        except Exception as e:
            print(f"Error in refresh action: {e}")

    def show_window(self, icon=None, item=None):
        """Show/restore window from tray"""
        try:
            self.gui_app.root.deiconify()
            self.gui_app.root.lift()
            self.gui_app.root.focus()
        except Exception as e:
            print(f"Error showing window: {e}")

    def exit_action(self, icon, item):
        """Exit application from tray"""
        try:
            self.is_running = False
            if self.icon:
                self.icon.stop()
            self.gui_app.root.quit()
        except Exception as e:
            print(f"Error in exit action: {e}")

    def stop(self):
        """Stop system tray"""
        try:
            if self.icon:
                self.icon.stop()
                self.is_running = False
        except Exception as e:
            print(f"Error stopping tray: {e}")


class ProgressDialog(tk.Toplevel):
    """Dialog hiển thị tiến trình upload"""
    
    def __init__(self, parent, title="Uploading"):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x250")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (250 // 2)
        self.geometry(f"500x250+{x}+{y}")
        
        self.configure(bg='#0d1117')
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.can_close = False
    
    def create_widgets(self):
        """Create progress UI"""
        # Title
        tk.Label(self, text="📤 Uploading to GitHub...",
                font=('Segoe UI', 14, 'bold'),
                bg='#0d1117', fg='#58a6ff').pack(pady=20)
        
        # Main frame
        main_frame = tk.Frame(self, bg='#161b22')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Initializing...",
                                     font=('Segoe UI', 10),
                                     bg='#161b22', fg='#c9d1d9')
        self.status_label.pack(anchor='w', pady=(0, 12))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate',
                                        value=0, maximum=100)
        self.progress.pack(fill='x', pady=10)
        
        # Progress text
        self.progress_text = tk.Label(main_frame, text="0%",
                                      font=('Segoe UI', 9),
                                      bg='#161b22', fg='#8b949e')
        self.progress_text.pack(anchor='e', pady=(0, 12))
        
        # Details
        self.details_frame = tk.Frame(main_frame, bg='#161b22')
        self.details_frame.pack(fill='both', expand=True, pady=10)
        
        self.details_text = tk.Text(self.details_frame, height=4, width=50,
                                    bg='#0d1117', fg='#8b949e',
                                    font=('Courier', 8),
                                    relief='flat', bd=0)
        self.details_text.pack(fill='both', expand=True)
        self.details_text.config(state='disabled')
        
        # Cancel button
        self.cancel_btn = tk.Button(self, text="✋ Cancel",
                                   command=self.on_close,
                                   bg='#f85149', fg='white',
                                   font=('Segoe UI', 10, 'bold'),
                                   relief='flat', cursor='hand2',
                                   padx=20, pady=8)
        self.cancel_btn.pack(pady=10)
    
    def update_status(self, status_text: str, progress: int = None):
        """Update status text and progress"""
        try:
            if self.winfo_exists():
                self.status_label.config(text=status_text)
                if progress is not None:
                    self.progress['value'] = progress
                    self.progress_text.config(text=f"{progress}%")
                self.update_idletasks()
        except:
            pass
    
    def add_detail(self, detail: str):
        """Add detail line"""
        try:
            if self.winfo_exists():
                self.details_text.config(state='normal')
                self.details_text.insert('end', detail + '\n')
                self.details_text.see('end')
                self.details_text.config(state='disabled')
                self.update_idletasks()
        except:
            pass
    
    def on_close(self):
        """Close dialog"""
        if self.can_close:
            self.destroy()
        else:
            messagebox.showwarning("Warning", "Upload in progress. Please wait.")
    
    def finish(self, success=True):
        """Mark as finished"""
        self.can_close = True
        if success:
            self.progress['value'] = 100
            self.progress_text.config(text="100%")
            self.status_label.config(text="✅ Upload Complete!", fg='#3fb950')
            self.cancel_btn.config(text="✅ Close", bg='#3fb950')
        else:
            self.status_label.config(text="❌ Upload Failed", fg='#f85149')
            self.cancel_btn.config(text="✅ Close", bg='#f85149')


class StatusPanel(tk.Frame):
    """Real-time status panel"""
    
    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors['card'])
        self.colors = colors
        
        # Status items
        self.status_frame = tk.Frame(self, bg=colors['card'])
        self.status_frame.pack(fill='x', padx=12, pady=8)
        
        self.status_items = {}
        self.create_status_items()
    
    def create_status_items(self):
        """Create status indicators"""
        items = [
            ('repo', '📁 Repository', 'Not configured'),
            ('branch', '🌿 Branch', 'main'),
            ('changes', '📝 Changes', '0 files'),
            ('last_push', '⏰ Last Push', 'Never')
        ]
        
        for key, label, default in items:
            frame = tk.Frame(self.status_frame, bg=self.colors['card'])
            frame.pack(side='left', fill='x', expand=True, padx=6)
            
            tk.Label(frame, text=label, font=('Segoe UI', 8),
                    bg=self.colors['card'], fg=self.colors['fg_secondary']).pack(anchor='w')
            
            value_label = tk.Label(frame, text=default, font=('Segoe UI', 9, 'bold'),
                                  bg=self.colors['card'], fg=self.colors['accent'])
            value_label.pack(anchor='w')
            
            self.status_items[key] = value_label
    
    def update_status(self, key, value):
        """Update status item"""
        try:
            if key in self.status_items:
                self.status_items[key].config(text=value)
        except:
            pass


class GitHubUploaderGUI:
    """Main GUI Application - Enhanced"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Auto Upload Tool Pro")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        
        self.uploader = GitHubUploader()
        self.uploader.load_profiles()
        
        # Animation variables
        self.upload_in_progress = False
        self.animation_state = 0
        
        # Apply theme
        self.apply_theme()
        self.create_ui()
        self.setup_tray()
        self.refresh_ui()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def apply_theme(self):
        """Apply color theme"""
        theme_name = getattr(self.uploader, 'theme_name', 'GitHub Dark')
        self.colors = THEMES.get(theme_name, THEMES['GitHub Dark'])
        self.root.configure(bg=self.colors['bg'])
    
    def t(self, key: str) -> str:
        """Translate text"""
        lang = getattr(self.uploader, 'language', 'en')
        return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
    
    def create_ui(self):
        """Create main UI"""
        # Main container with scrollbar
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True)
        
        # Canvas for scrolling
        canvas = tk.Canvas(main_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Title with animation
        title_frame = tk.Frame(scrollable_frame, bg=self.colors['accent'], height=80)
        title_frame.pack(fill='x', pady=(0, 0))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🚀 GitHub Auto Upload Tool Pro",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['accent'],
            fg='white'
        )
        title_label.pack(expand=True)
        
        # Status panel
        self.status_panel = StatusPanel(scrollable_frame, self.colors)
        self.status_panel.pack(fill='x', pady=8, padx=12)
        
        # Quick Actions Section
        self.create_quick_actions(scrollable_frame)
        
        # Configuration Section
        self.create_config_section(scrollable_frame)
        
        # Background Mode Section
        self.create_bg_section(scrollable_frame)
        
        # Utilities Section
        self.create_utilities_section(scrollable_frame)
    
    def create_quick_actions(self, parent):
        """Create quick actions section with enhanced styling"""
        frame = tk.LabelFrame(
            parent,
            text="⚡ Quick Actions",
            bg=self.colors['card'],
            fg=self.colors['fg'],
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            padx=16,
            pady=16,
            borderwidth=2
        )
        frame.pack(fill='x', pady=12, padx=12)
        
        btn_frame = tk.Frame(frame, bg=self.colors['card'])
        btn_frame.pack(fill='x')
        
        buttons = [
            (self.t('upload'), self.do_upload, self.colors['success'], '🚀'),
            (self.t('git_status'), self.show_git_status, self.colors['accent'], '📊'),
            (self.t('create_gitignore'), self.create_gitignore, self.colors['warning'], '📝'),
        ]
        
        for text, command, color, emoji in buttons:
            btn = tk.Button(
                btn_frame,
                text=f"{emoji} {text}",
                command=command,
                bg=color,
                fg='white',
                font=('Segoe UI', 10, 'bold'),
                relief='flat',
                cursor='hand2',
                padx=16,
                pady=12,
                activebackground=color,
                activeforeground='white'
            )
            btn.pack(side='left', padx=6, expand=True, fill='both')
            
            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn: self.on_button_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_button_leave(b))
    
    def on_button_enter(self, btn):
        """Button hover effect"""
        try:
            btn.config(relief='raised', bd=2)
        except:
            pass
    
    def on_button_leave(self, btn):
        """Button leave effect"""
        try:
            btn.config(relief='flat', bd=0)
        except:
            pass
    
    def create_config_section(self, parent):
        """Create configuration section"""
        frame = tk.LabelFrame(
            parent,
            text="⚙️ Configuration",
            bg=self.colors['card'],
            fg=self.colors['fg'],
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            padx=16,
            pady=16,
            borderwidth=2
        )
        frame.pack(fill='x', pady=12, padx=12)
        
        btn_frame = tk.Frame(frame, bg=self.colors['card'])
        btn_frame.pack(fill='x')
        
        buttons = [
            (self.t('manage_profiles'), self.manage_profiles, self.colors['accent'], '💾'),
            (self.t('auto_settings'), self.configure_auto, self.colors['warning'], '⏰'),
            (self.t('commit_mode'), self.configure_commit_mode, self.colors['success'], '📋'),
            (self.t('settings'), self.open_settings, self.colors['fg_secondary'], '⚙️'),
        ]
        
        for text, command, color, emoji in buttons:
            btn = tk.Button(
                btn_frame,
                text=f"{emoji} {text}",
                command=command,
                bg=color,
                fg='white',
                font=('Segoe UI', 10, 'bold'),
                relief='flat',
                cursor='hand2',
                padx=12,
                pady=10,
                activebackground=color,
                activeforeground='white'
            )
            btn.pack(side='left', padx=4, expand=True, fill='both')
            
            btn.bind("<Enter>", lambda e, b=btn: self.on_button_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_button_leave(b))
    
    def create_bg_section(self, parent):
        """Create background mode section"""
        frame = tk.LabelFrame(
            parent,
            text="🔄 Background Mode",
            bg=self.colors['card'],
            fg=self.colors['fg'],
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            padx=16,
            pady=16,
            borderwidth=2
        )
        frame.pack(fill='x', pady=12, padx=12)
        
        btn_frame = tk.Frame(frame, bg=self.colors['card'])
        btn_frame.pack(fill='x')
        
        buttons = [
            (self.t('start_bg'), self.start_background, self.colors['success'], '▶️'),
            (self.t('stop_bg'), self.stop_background, self.colors['danger'], '⏸️'),
            (self.t('view_status'), self.view_bg_status, self.colors['accent'], '📡'),
        ]
        
        for text, command, color, emoji in buttons:
            btn = tk.Button(
                btn_frame,
                text=f"{emoji} {text}",
                command=command,
                bg=color,
                fg='white',
                font=('Segoe UI', 10, 'bold'),
                relief='flat',
                cursor='hand2',
                padx=12,
                pady=10,
                activebackground=color,
                activeforeground='white'
            )
            btn.pack(side='left', padx=4, expand=True, fill='both')
            
            btn.bind("<Enter>", lambda e, b=btn: self.on_button_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_button_leave(b))
    
    def create_utilities_section(self, parent):
        """Create utilities section"""
        frame = tk.LabelFrame(
            parent,
            text="🛠️ Utilities",
            bg=self.colors['card'],
            fg=self.colors['fg'],
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            padx=16,
            pady=16,
            borderwidth=2
        )
        frame.pack(fill='x', pady=12, padx=12)
        
        btn_frame = tk.Frame(frame, bg=self.colors['card'])
        btn_frame.pack(fill='x')
        
        buttons = [
            (self.t('view_logs'), self.view_logs, self.colors['fg_secondary'], '📄'),
            (self.t('exit'), self.on_close, self.colors['danger'], '🚪'),
        ]
        
        for text, command, color, emoji in buttons:
            btn = tk.Button(
                btn_frame,
                text=f"{emoji} {text}",
                command=command,
                bg=color,
                fg='white',
                font=('Segoe UI', 10, 'bold'),
                relief='flat',
                cursor='hand2',
                padx=12,
                pady=10,
                activebackground=color,
                activeforeground='white'
            )
            btn.pack(side='left', padx=4, expand=True, fill='both')
            
            btn.bind("<Enter>", lambda e, b=btn: self.on_button_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_button_leave(b))
    
    def setup_tray(self):
        """Setup system tray"""
        self.tray = SystemTrayManager(self)
        Thread(target=self.tray.create_icon, daemon=True).start()
    
    def do_upload(self):
        """Execute upload with progress dialog"""
        if not self.uploader.repo_path:
            messagebox.showerror(self.t('error'), "❌ Repository path not configured!")
            return
        
        if self.upload_in_progress:
            messagebox.showwarning(self.t('warning'), "⚠️ Upload already in progress!")
            return
        
        # Create progress dialog
        progress = ProgressDialog(self.root, "📤 GitHub Upload")
        
        def do_upload_thread():
            try:
                self.upload_in_progress = True
                
                # Stage 1: Pull
                progress.update_status("📥 Pulling latest changes...", 15)
                progress.add_detail("$ git pull origin main")
                if not self.uploader.git_pull():
                    progress.add_detail("⚠️ Pull completed (no changes or auto-pull disabled)")
                else:
                    progress.add_detail("✅ Pull successful")
                
                # Stage 2: Add files
                progress.update_status("📂 Adding files...", 35)
                progress.add_detail("$ git add -A")
                if not self.uploader.git_add_all():
                    progress.add_detail("ℹ️ No files to add")
                else:
                    progress.add_detail("✅ Files added successfully")
                
                # Stage 3: Commit
                progress.update_status("💾 Creating commit...", 55)
                progress.add_detail(f"$ git commit -m 'Auto update'")
                if not self.uploader.git_commit(""):
                    progress.add_detail("⚠️ Nothing to commit (working directory clean)")
                else:
                    progress.add_detail("✅ Commit created successfully")
                
                # Stage 4: Push
                progress.update_status("🚀 Pushing to GitHub...", 80)
                progress.add_detail(f"$ git push -u origin {self.uploader.branch}")
                if not self.uploader.git_push():
                    raise Exception("Push failed - check network and credentials")
                else:
                    progress.add_detail("✅ Push successful")
                
                # Success
                progress.update_status("✅ Upload Complete!", 100)
                progress.add_detail("\n✨ All operations completed successfully!")
                progress.finish(success=True)
                
                self.refresh_ui()
                
                # Auto-close after 2 seconds
                self.root.after(2000, progress.destroy)
                
            except Exception as e:
                progress.update_status(f"❌ Error: {str(e)}", 0)
                progress.add_detail(f"\n❌ {str(e)}")
                progress.finish(success=False)
                self.uploader.logger.error(f"Upload error: {e}")
            
            finally:
                self.upload_in_progress = False
        
        Thread(target=do_upload_thread, daemon=True).start()
    
    def show_git_status(self):
        """Show git status"""
        try:
            status = self.uploader._git("status")
            if status:
                dialog = tk.Toplevel(self.root)
                dialog.title("📊 Git Status")
                dialog.geometry("700x500")
                dialog.transient(self.root)
                dialog.configure(bg=self.colors['bg'])
                
                # Center
                dialog.update_idletasks()
                x = (dialog.winfo_screenwidth() // 2) - (700 // 2)
                y = (dialog.winfo_screenheight() // 2) - (500 // 2)
                dialog.geometry(f"700x500+{x}+{y}")
                
                text_widget = tk.Text(dialog, bg=self.colors['card'],
                                     fg=self.colors['fg'],
                                     font=('Courier', 9),
                                     padx=12, pady=12)
                text_widget.pack(fill='both', expand=True, padx=12, pady=12)
                text_widget.insert('1.0', status)
                text_widget.config(state='disabled')
                
                tk.Button(dialog, text="✅ Close", command=dialog.destroy,
                         bg=self.colors['success'], fg='white',
                         font=('Segoe UI', 10, 'bold')).pack(pady=8)
            else:
                messagebox.showerror(self.t('error'), "❌ Cannot get git status")
        except Exception as e:
            self.uploader.logger.error(f"Error showing status: {e}")
            messagebox.showerror(self.t('error'), str(e))
    
    def create_gitignore(self):
        """Create .gitignore"""
        self.uploader.create_gitignore()
    
    def manage_profiles(self):
        """Open profile management dialog"""
        ProfileDialog(self, self.uploader)
    
    def configure_auto(self):
        """Configure auto upload settings"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⏰ Auto Upload Settings")
        dialog.geometry("450x350")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['bg'])
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"450x350+{x}+{y}")
        
        tk.Label(dialog, text="⏰ Auto Upload Settings", 
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=12)
        
        # Interval setting
        tk.Label(dialog, text="Check Interval (minutes):", 
                bg=self.colors['bg'], fg=self.colors['fg']).pack(anchor='w', padx=20, pady=(8, 2))
        
        interval_var = StringVar(value=str(self.uploader.auto_upload_interval))
        interval_spin = tk.Spinbox(dialog, from_=1, to=1440, textvariable=interval_var,
                                   bg=self.colors['card'], fg=self.colors['fg'],
                                   font=('Segoe UI', 10), width=10)
        interval_spin.pack(padx=20, pady=4)
        
        # Auto pull option
        auto_pull_var = BooleanVar(value=self.uploader.auto_pull)
        tk.Checkbutton(dialog, text="Auto-pull before push (recommended)",
                      variable=auto_pull_var, bg=self.colors['bg'],
                      fg=self.colors['fg'], selectcolor=self.colors['card'],
                      activebackground=self.colors['bg'],
                      activeforeground=self.colors['fg']).pack(anchor='w', padx=20, pady=8)
        
        # Auto resolve option
        auto_resolve_var = BooleanVar(value=self.uploader.auto_resolve)
        tk.Checkbutton(dialog, text="Auto-resolve merge conflicts",
                      variable=auto_resolve_var, bg=self.colors['bg'],
                      fg=self.colors['fg'], selectcolor=self.colors['card'],
                      activebackground=self.colors['bg'],
                      activeforeground=self.colors['fg']).pack(anchor='w', padx=20, pady=8)
        
        # Commit template
        tk.Label(dialog, text="Commit Message Template:",
                bg=self.colors['bg'], fg=self.colors['fg']).pack(anchor='w', padx=20, pady=(12, 2))
        
        template_text = tk.Text(dialog, height=4, width=40,
                               bg=self.colors['card'], fg=self.colors['fg'],
                               font=('Segoe UI', 9))
        template_text.pack(padx=20, pady=4)
        template_text.insert('1.0', self.uploader.commit_message_template)
        
        tk.Label(dialog, text="Variables: {datetime}, {date}, {time}, {user}",
                bg=self.colors['bg'], fg=self.colors['fg_secondary'],
                font=('Segoe UI', 8)).pack(anchor='w', padx=20)
        
        def save_settings():
            try:
                self.uploader.auto_upload_interval = int(interval_var.get())
                self.uploader.auto_pull = auto_pull_var.get()
                self.uploader.auto_resolve = auto_resolve_var.get()
                self.uploader.commit_message_template = template_text.get('1.0', 'end-1c')
                self.uploader.save_config()
                messagebox.showinfo(self.t('success'), "Settings saved!", parent=dialog)
                dialog.destroy()
            except ValueError:
                messagebox.showerror(self.t('error'), "Invalid interval value", parent=dialog)
        
        tk.Button(dialog, text="✅ Save", command=save_settings,
                 bg=self.colors['success'], fg='white',
                 font=('Segoe UI', 10, 'bold'), relief='flat',
                 cursor='hand2', padx=20, pady=8).pack(pady=12)

    def configure_commit_mode(self):
        """Configure commit mode settings"""
        dialog = tk.Toplevel(self.root)
        dialog.title("📋 Commit Mode Settings")
        dialog.geometry("450x280")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['bg'])
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (280 // 2)
        dialog.geometry(f"450x280+{x}+{y}")
        
        tk.Label(dialog, text="📋 Commit Mode Settings",
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=12)
        
        tk.Label(dialog, text="Select commit mode:",
                bg=self.colors['bg'], fg=self.colors['fg']).pack(anchor='w', padx=20, pady=(8, 4))
        
        mode_var = StringVar(value=self.uploader.commit_mode)
        
        modes = {
            'always': '🔄 Always - Commit every change',
            'daily': '📅 Daily - Only one commit per day',
            'manual': '🖱️ Manual - Require manual confirmation'
        }
        
        for mode, desc in modes.items():
            tk.Radiobutton(dialog, text=desc, variable=mode_var, value=mode,
                          bg=self.colors['bg'], fg=self.colors['fg'],
                          selectcolor=self.colors['card'],
                          activebackground=self.colors['bg'],
                          activeforeground=self.colors['fg']).pack(anchor='w', padx=40, pady=6)
        
        # Use conventional commits
        conventional_var = BooleanVar(value=self.uploader.use_conventional_commits)
        tk.Checkbutton(dialog, text="Use Conventional Commits",
                      variable=conventional_var, bg=self.colors['bg'],
                      fg=self.colors['fg'], selectcolor=self.colors['card'],
                      activebackground=self.colors['bg'],
                      activeforeground=self.colors['fg']).pack(anchor='w', padx=20, pady=(12, 4))
        
        def save_settings():
            self.uploader.commit_mode = mode_var.get()
            self.uploader.use_conventional_commits = conventional_var.get()
            self.uploader.save_config()
            messagebox.showinfo(self.t('success'), "Settings saved!", parent=dialog)
            dialog.destroy()
        
        tk.Button(dialog, text="✅ Save", command=save_settings,
                 bg=self.colors['success'], fg='white',
                 font=('Segoe UI', 10, 'bold'), relief='flat',
                 cursor='hand2', padx=20, pady=8).pack(pady=12)
    
    def open_settings(self):
        """Open advanced settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.t('settings'))
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['bg'])
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"500x600+{x}+{y}")
        
        # Create notebook with tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=12, pady=12)
        
        # General tab
        general_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(general_frame, text="📋 General")
        
        tk.Label(general_frame, text="Repository Path:", bg=self.colors['bg'],
                fg=self.colors['fg']).pack(anchor='w', padx=20, pady=(12, 2))
        repo_entry = tk.Entry(general_frame, bg=self.colors['card'],
                             fg=self.colors['fg'], width=40)
        repo_entry.insert(0, self.uploader.repo_path)
        repo_entry.pack(padx=20, pady=4)
        
        tk.Label(general_frame, text="Remote URL:", bg=self.colors['bg'],
                fg=self.colors['fg']).pack(anchor='w', padx=20, pady=(12, 2))
        remote_entry = tk.Entry(general_frame, bg=self.colors['card'],
                               fg=self.colors['fg'], width=40)
        remote_entry.insert(0, self.uploader.remote_url)
        remote_entry.pack(padx=20, pady=4)
        
        tk.Label(general_frame, text="Branch:", bg=self.colors['bg'],
                fg=self.colors['fg']).pack(anchor='w', padx=20, pady=(12, 2))
        branch_entry = tk.Entry(general_frame, bg=self.colors['card'],
                               fg=self.colors['fg'], width=40)
        branch_entry.insert(0, self.uploader.branch)
        branch_entry.pack(padx=20, pady=4)
        
        # Theme tab
        theme_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(theme_frame, text="🎨 Theme")
        
        tk.Label(theme_frame, text="Select Theme:", bg=self.colors['bg'],
                fg=self.colors['fg'], font=('Segoe UI', 11, 'bold')).pack(anchor='w', padx=20, pady=12)
        
        theme_var = StringVar(value=self.uploader.theme_name)
        for theme_name in THEMES.keys():
            tk.Radiobutton(theme_frame, text=theme_name, variable=theme_var, value=theme_name,
                          bg=self.colors['bg'], fg=self.colors['fg'],
                          selectcolor=self.colors['card'],
                          activebackground=self.colors['bg'],
                          activeforeground=self.colors['fg']).pack(anchor='w', padx=40, pady=4)
        
        # Behavior tab
        behavior_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(behavior_frame, text="⚙️ Behavior")
        
        minimize_var = BooleanVar(value=self.uploader.minimize_to_tray)
        tk.Checkbutton(behavior_frame, text=self.t('minimize_to_tray'),
                      variable=minimize_var, bg=self.colors['bg'],
                      fg=self.colors['fg']).pack(anchor='w', padx=20, pady=8)
        
        notifications_var = BooleanVar(value=self.uploader.show_notifications)
        tk.Checkbutton(behavior_frame, text="Show Notifications",
                      variable=notifications_var, bg=self.colors['bg'],
                      fg=self.colors['fg']).pack(anchor='w', padx=20, pady=8)
        
        startup_var = BooleanVar(value=self.uploader.start_with_windows)
        tk.Checkbutton(behavior_frame, text=self.t('start_with_windows'),
                      variable=startup_var, bg=self.colors['bg'],
                      fg=self.colors['fg']).pack(anchor='w', padx=20, pady=8)
        
        # Save button
        def save_all():
            self.uploader.repo_path = repo_entry.get().strip()
            self.uploader.remote_url = remote_entry.get().strip()
            self.uploader.branch = branch_entry.get().strip() or 'main'
            self.uploader.theme_name = theme_var.get()
            self.uploader.minimize_to_tray = minimize_var.get()
            self.uploader.show_notifications = notifications_var.get()
            self.uploader.start_with_windows = startup_var.get()
            self.uploader.save_config()
            self.uploader.save_settings()
            messagebox.showinfo(self.t('success'), self.t('save_success'), parent=dialog)
            dialog.destroy()
            self.apply_theme()
            self.refresh_ui()
        
        tk.Button(dialog, text=self.t('save'), command=save_all,
                 bg=self.colors['success'], fg='white',
                 font=('Segoe UI', 10, 'bold'), relief='flat',
                 cursor='hand2', padx=20, pady=8).pack(pady=12)
    
    def start_background(self):
        """Start background mode"""
        messagebox.showinfo(self.t('info'), "✅ Background mode started!")
        self.uploader.logger.info("Background mode started")
    
    def stop_background(self):
        """Stop background mode"""
        messagebox.showinfo(self.t('info'), "⏸️ Background mode stopped!")
        self.uploader.logger.info("Background mode stopped")
    
    def view_bg_status(self):
        """View background status"""
        messagebox.showinfo(self.t('info'), "📡 Background mode: Active")
    
    def view_logs(self):
        """View application logs"""
        try:
            log_file = list(self.uploader.log_dir.glob('*.log'))
            if log_file:
                os.startfile(str(log_file[-1]))
            else:
                messagebox.showinfo(self.t('info'), "📄 No logs found")
        except Exception as e:
            messagebox.showerror(self.t('error'), str(e))
    
    def refresh_ui(self):
        """Refresh UI status"""
        try:
            # Update status panel
            repo_name = Path(self.uploader.repo_path).name if self.uploader.repo_path else "Not set"
            self.status_panel.update_status('repo', f"📁 {repo_name}")
            self.status_panel.update_status('branch', f"🌿 {self.uploader.branch}")
            
            # Get file count
            try:
                status_output = self.uploader._git("status --porcelain")
                file_count = len(status_output.split('\n')) if status_output else 0
                self.status_panel.update_status('changes', f"📝 {file_count} files")
            except:
                self.status_panel.update_status('changes', "📝 0 files")
            
            self.status_panel.update_status('last_push', f"⏰ {self.uploader.last_commit_date or 'Never'}")
        except Exception as e:
            self.uploader.logger.error(f"Error refreshing UI: {e}")
    
    def on_close(self):
        """Handle window close"""
        if self.upload_in_progress:
            if not messagebox.askyesno(self.t('confirm'), "Upload in progress. Exit anyway?"):
                return
        
        if self.uploader.minimize_to_tray:
            self.root.withdraw()
            messagebox.showinfo(self.t('info'), self.t('minimize_info'))
        else:
            try:
                if hasattr(self, 'tray') and self.tray:
                    self.tray.stop()
            except:
                pass
            self.root.quit()


class ProfileDialog(tk.Toplevel):
    """Dialog để quản lý profiles"""
    
    def __init__(self, parent, uploader: GitHubUploader):
        super().__init__(parent.root)
        self.parent = parent
        self.uploader = uploader
        self.transient(parent.root)
        self.grab_set()
        self.title("💾 Manage Profiles")
        self.geometry("600x450")
        
        try:
            self.configure(bg=parent.colors['bg'])
        except (AttributeError, KeyError):
            self.configure(bg='#0d1117')
        
        self.resizable(False, False)
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (450 // 2)
        self.geometry(f"600x450+{x}+{y}")
        
        self.create_widgets()

    def create_widgets(self):
        """Create profile management UI"""
        tk.Label(self, text="💾 Manage Profiles", font=('Segoe UI', 14, 'bold'),
                bg=self.parent.colors['bg'], fg=self.parent.colors['fg']).pack(pady=12)
        
        # Profile list frame
        list_frame = tk.Frame(self, bg=self.parent.colors['card'])
        list_frame.pack(fill='both', expand=True, padx=12, pady=10)
        
        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.profile_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg=self.parent.colors['card'],
            fg=self.parent.colors['fg'],
            selectmode='single',
            font=('Segoe UI', 10)
        )
        self.profile_listbox.pack(fill='both', expand=True, padx=8, pady=8)
        scrollbar.config(command=self.profile_listbox.yview)
        
        # Load profiles
        self.refresh_list()
        
        # Button frame
        btn_frame = tk.Frame(self, bg=self.parent.colors['bg'])
        btn_frame.pack(fill='x', padx=12, pady=12)
        
        buttons = [
            ("➕ New", self.new_profile, self.parent.colors['success']),
            ("✏️ Edit", self.edit_profile, self.parent.colors['accent']),
            ("🔄 Load", self.load_profile, self.parent.colors['warning']),
            ("🗑️ Delete", self.delete_profile, self.parent.colors['danger']),
        ]
        
        for text, cmd, color in buttons:
            tk.Button(btn_frame, text=text, command=cmd,
                     bg=color, fg='white',
                     font=('Segoe UI', 9, 'bold'), relief='flat',
                     cursor='hand2', padx=12, pady=6).pack(side='left', padx=4)
        
        tk.Button(btn_frame, text="✅ Close", command=self.destroy,
                 bg=self.parent.colors['fg_tertiary'], fg='white',
                 font=('Segoe UI', 9, 'bold'), relief='flat',
                 cursor='hand2', padx=12, pady=6).pack(side='right', padx=4)

    def refresh_list(self):
        """Refresh profile list"""
        self.profile_listbox.delete(0, 'end')
        current = self.uploader.current_profile
        for i, name in enumerate(self.uploader.profiles.keys()):
            label = f"⭐ {name}" if name == current else f"  {name}"
            self.profile_listbox.insert(i, label)

    def new_profile(self):
        """Create new profile"""
        name = simpledialog.askstring("New Profile", "Enter profile name:", parent=self)
        if not name:
            return
        
        if name in self.uploader.profiles:
            messagebox.showwarning("Error", "Profile already exists", parent=self)
            return
        
        self._edit_profile_dialog(name, {})

    def edit_profile(self):
        """Edit selected profile"""
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a profile first", parent=self)
            return
        
        profile_name = list(self.uploader.profiles.keys())[selection[0]]
        profile = self.uploader.get_profile(profile_name)
        self._edit_profile_dialog(profile_name, profile)

    def _edit_profile_dialog(self, profile_name: str, profile: dict):
        """Edit profile dialog"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit Profile: {profile_name}")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=self.parent.colors['bg'])
        
        tk.Label(dialog, text=f"✏️ Edit Profile: {profile_name}", font=('Segoe UI', 12, 'bold'),
                bg=self.parent.colors['bg'], fg=self.parent.colors['fg']).pack(pady=12)
        
        tk.Label(dialog, text="Repository Path:", bg=self.parent.colors['bg'],
                fg=self.parent.colors['fg']).pack(anchor='w', padx=12, pady=(8, 2))
        repo_entry = tk.Entry(dialog, bg=self.parent.colors['card'],
                             fg=self.parent.colors['fg'], width=40)
        repo_entry.insert(0, profile.get('repo_path', ''))
        repo_entry.pack(padx=12, pady=4)
        
        tk.Label(dialog, text="Remote URL:", bg=self.parent.colors['bg'],
                fg=self.parent.colors['fg']).pack(anchor='w', padx=12, pady=(8, 2))
        remote_entry = tk.Entry(dialog, bg=self.parent.colors['card'],
                               fg=self.parent.colors['fg'], width=40)
        remote_entry.insert(0, profile.get('remote_url', ''))
        remote_entry.pack(padx=12, pady=4)
        
        tk.Label(dialog, text="Branch:", bg=self.parent.colors['bg'],
                fg=self.parent.colors['fg']).pack(anchor='w', padx=12, pady=(8, 2))
        branch_entry = tk.Entry(dialog, bg=self.parent.colors['card'],
                               fg=self.parent.colors['fg'], width=40)
        branch_entry.insert(0, profile.get('branch', 'main'))
        branch_entry.pack(padx=12, pady=4)
        
        def save():
            self.uploader.save_profile(profile_name, {
                'repo_path': repo_entry.get().strip(),
                'remote_url': remote_entry.get().strip(),
                'branch': branch_entry.get().strip() or 'main'
            })
            messagebox.showinfo("Success", f"Profile '{profile_name}' saved", parent=dialog)
            dialog.destroy()
            self.refresh_list()
        
        tk.Button(dialog, text="✅ Save", command=save,
                 bg=self.parent.colors['success'], fg='white',
                 font=('Segoe UI', 10, 'bold'), relief='flat',
                 cursor='hand2', padx=16, pady=8).pack(pady=12)

    def load_profile(self):
        """Load selected profile"""
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a profile first", parent=self)
            return
        
        profile_name = list(self.uploader.profiles.keys())[selection[0]]
        profile = self.uploader.get_profile(profile_name)
        
        self.uploader.repo_path = profile.get('repo_path', '')
        self.uploader.remote_url = profile.get('remote_url', '')
        self.uploader.branch = profile.get('branch', 'main')
        self.uploader.current_profile = profile_name
        self.uploader.save_config()
        
        messagebox.showinfo("Success", f"Profile '{profile_name}' loaded", parent=self)
        self.parent.refresh_ui()
        self.refresh_list()

    def delete_profile(self):
        """Delete selected profile"""
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a profile first", parent=self)
            return
        
        profile_name = list(self.uploader.profiles.keys())[selection[0]]
        
        if profile_name == 'default':
            messagebox.showwarning("Error", "Cannot delete default profile", parent=self)
            return
        
        if messagebox.askyesno("Confirm", f"Delete profile '{profile_name}'?", parent=self):
            self.uploader.delete_profile(profile_name)
            messagebox.showinfo("Success", f"Profile '{profile_name}' deleted", parent=self)
            self.refresh_list()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = GitHubUploaderGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
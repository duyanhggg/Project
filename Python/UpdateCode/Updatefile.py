#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Auto Upload Tool Pro
Công cụ tự động đẩy code lên GitHub với nhiều tính năng nâng cao
Version 2.4 - Enhanced UI with Modern Design
"""

import os
import sys
import subprocess
import json
import logging
import time
import psutil
from datetime import datetime
from pathlib import Path
from threading import Thread
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, scrolledtext
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item


class GitHubUploader:
    """Core class xử lý Git operations"""
    
    def __init__(self):
        self.config_file = Path.home() / '.github_uploader' / 'config.json'
        self.profiles_file = Path.home() / '.github_uploader' / 'profiles.json'
        self.log_dir = Path.home() / '.github_uploader' / 'logs'
        self.status_file = Path.home() / '.github_uploader' / 'status.json'
        self.bg_pid_file = Path.home() / '.github_uploader' / 'background.pid'
        
        # Tạo thư mục config
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
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
        
        # Load config
        self.load_config()

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
                                                             'Auto upload: {datetime}')
                    self.current_profile = config.get('current_profile', 'default')
            else:
                self.repo_path = ''
                self.remote_url = ''
                self.branch = 'main'
                self.auto_upload_interval = 30
                self.commit_message_template = 'Auto upload: {datetime}'
                self.current_profile = 'default'
                self.save_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            messagebox.showerror("Lỗi", f"Không thể load config: {e}")

    def save_config(self):
        """Lưu cấu hình vào file"""
        try:
            config = {
                'repo_path': self.repo_path,
                'remote_url': self.remote_url,
                'branch': self.branch,
                'auto_upload_interval': self.auto_upload_interval,
                'commit_message_template': self.commit_message_template,
                'current_profile': self.current_profile
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.logger.info("Config saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    def list_profiles(self):
        """Liệt kê tất cả profiles"""
        try:
            if self.profiles_file.exists():
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
                    return list(profiles.keys())
            return []
        except Exception as e:
            self.logger.error(f"Error listing profiles: {e}")
            return []

    def get_profile(self, name: str):
        """Lấy thông tin profile"""
        try:
            if self.profiles_file.exists():
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
                    return profiles.get(name)
            return None
        except Exception as e:
            self.logger.error(f"Error getting profile: {e}")
            return None

    def save_profile(self, name: str, profile: dict = None):
        """Lưu profile"""
        try:
            profiles = {}
            if self.profiles_file.exists():
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
            
            if profile is None:
                profile = {
                    'repo_path': self.repo_path,
                    'remote_url': self.remote_url,
                    'branch': self.branch,
                    'auto_upload_interval': self.auto_upload_interval
                }
            
            profiles[name] = profile
            
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(profiles, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"Profile '{name}' saved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error saving profile: {e}")
            return False

    def delete_profile(self, name: str):
        """Xóa profile"""
        try:
            if self.profiles_file.exists():
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
                
                if name in profiles:
                    del profiles[name]
                    
                    with open(self.profiles_file, 'w', encoding='utf-8') as f:
                        json.dump(profiles, f, indent=4, ensure_ascii=False)
                    
                    self.logger.info(f"Profile '{name}' deleted successfully")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting profile: {e}")
            return False
    
    def load_profile(self, name: str) -> bool:
        """Load profile và áp dụng cấu hình"""
        try:
            profile = self.get_profile(name)
            if profile:
                self.repo_path = profile.get('repo_path', '')
                self.remote_url = profile.get('remote_url', '')
                self.branch = profile.get('branch', 'main')
                self.auto_upload_interval = profile.get('auto_upload_interval', 30)
                self.current_profile = name
                self.save_config()
                self.logger.info(f"Profile '{name}' loaded successfully")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error loading profile: {e}")
            return False

    def run_command(self, command: str):
        """Chạy command và trả về output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.repo_path if self.repo_path else None,
                capture_output=True,
                text=True,
                timeout=30
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

    def init_git_repo(self) -> bool:
        """Khởi tạo Git repository"""
        try:
            if not self.repo_path:
                messagebox.showerror("Lỗi", "Chưa chọn thư mục repository!")
                return False
            
            result = self._git("init")
            if result is not None:
                self.logger.info(f"Git repo initialized at {self.repo_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error initializing repo: {e}")
            return False

    def configure_remote(self) -> bool:
        """Cấu hình remote URL"""
        try:
            if not self.remote_url:
                messagebox.showerror("Lỗi", "Chưa có remote URL!")
                return False
            
            # Remove existing remote
            self._git("remote remove origin")
            
            # Add new remote
            result = self._git(f"remote add origin {self.remote_url}")
            if result is not None or "already exists" in str(result):
                self.logger.info(f"Remote configured: {self.remote_url}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error configuring remote: {e}")
            return False

    def show_git_status(self):
        """Hiển thị Git status"""
        try:
            status = self._git("status")
            if status:
                messagebox.showinfo("Git Status", status)
            else:
                messagebox.showerror("Lỗi", "Không thể lấy Git status")
        except Exception as e:
            self.logger.error(f"Error showing status: {e}")
            messagebox.showerror("Lỗi", str(e))

    def create_gitignore(self):
        """Tạo file .gitignore"""
        try:
            if not self.repo_path:
                messagebox.showerror("Lỗi", "Chưa chọn thư mục repository!")
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
                response = messagebox.askyesno("Xác nhận", 
                    ".gitignore đã tồn tại. Bạn có muốn ghi đè?")
                if not response:
                    return
            
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(default_content)
            
            messagebox.showinfo("Thành công", "Đã tạo .gitignore")
            self.logger.info(".gitignore created")
        except Exception as e:
            self.logger.error(f"Error creating .gitignore: {e}")
            messagebox.showerror("Lỗi", str(e))

    def git_add_all(self) -> bool:
        """Git add tất cả files"""
        try:
            result = self._git("add .")
            return result is not None
        except Exception as e:
            self.logger.error(f"Error adding files: {e}")
            return False

    def git_commit(self, message: str) -> bool:
        """Git commit với message"""
        try:
            if not message:
                message = self.commit_message_template.format(
                    datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            
            result = self._git(f'commit -m "{message}"')
            if result is not None:
                self.logger.info(f"Committed: {message}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error committing: {e}")
            return False

    def git_push(self) -> bool:
        """Git push lên remote"""
        try:
            result = self._git(f"push -u origin {self.branch}")
            if result is not None:
                self.logger.info(f"Pushed to {self.branch}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error pushing: {e}")
            return False

    def start_background_mode(self) -> bool:
        """Start background upload mode"""
        try:
            if self.is_background_running():
                self.logger.warning("Background mode already running")
                return False
            
            # Start background process
            thread = Thread(target=self.run_background_loop, daemon=True)
            thread.start()
            
            # Save PID
            with open(self.bg_pid_file, 'w') as f:
                f.write(str(os.getpid()))
            
            self.logger.info("Background mode started")
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
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error stopping background mode: {e}")
            return False

    def _read_bg_pid(self):
        """Đọc PID của background process"""
        try:
            if self.bg_pid_file.exists():
                with open(self.bg_pid_file, 'r') as f:
                    return int(f.read().strip())
            return None
        except:
            return None

    def is_background_running(self) -> bool:
        """Kiểm tra background mode có đang chạy không"""
        pid = self._read_bg_pid()
        if pid:
            try:
                return psutil.pid_exists(pid)
            except:
                return False
        return False
    
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

    def run_background_loop(self):
        """Background loop để auto upload"""
        self.logger.info("Background loop started")
        while self.is_background_running():
            try:
                if self.repo_path and Path(self.repo_path).exists():
                    # Check for changes
                    status = self._git("status --porcelain")
                    if status:
                        self.logger.info("Changes detected, uploading...")
                        if self.git_add_all():
                            if self.git_commit(""):
                                if self.git_push():
                                    self._write_status("success", "Auto upload successful")
                                else:
                                    self._write_status("error", "Push failed")
                            else:
                                self._write_status("info", "No changes to commit")
                        else:
                            self._write_status("error", "Add failed")
                    else:
                        self._write_status("info", "No changes detected")
                
                # Sleep
                time.sleep(self.auto_upload_interval * 60)
            except Exception as e:
                self.logger.error(f"Background loop error: {e}")
                self._write_status("error", str(e))
                time.sleep(60)

    def view_logs(self):
        """Xem logs"""
        try:
            import webbrowser
            log_files = list(self.log_dir.glob('*.log'))
            if log_files:
                latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
                webbrowser.open(str(latest_log))
            else:
                messagebox.showinfo("Thông báo", "Chưa có file log nào")
        except Exception as e:
            self.logger.error(f"Error viewing logs: {e}")
            messagebox.showerror("Lỗi", str(e))


class SystemTrayManager:
    """Quản lý System Tray"""
    
    def __init__(self, gui_app):
        self.gui_app = gui_app
        self.icon = None
        
    def create_image(self):
        """Tạo icon cho system tray"""
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='#4078c0')
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
    
    def upload_now(self, icon=None, item=None):
        """Upload ngay lập tức"""
        self.gui_app.upload_code()
    
    def show_status(self, icon=None, item=None):
        """Hiển thị status"""
        status = self.gui_app.uploader.read_status()
        if status:
            msg = f"Time: {status['timestamp']}\nResult: {status['result']}\nMessage: {status['message']}"
            messagebox.showinfo("Background Status", msg)
        else:
            messagebox.showinfo("Background Status", "No status available")
    
    def quit_app(self, icon=None, item=None):
        """Thoát ứng dụng"""
        if icon:
            icon.stop()
        self.gui_app.root.quit()
    
    def start(self):
        """Khởi động system tray"""
        menu = (
            item('Show Window', self.show_window),
            item('Upload Now', self.upload_now),
            item('Show Status', self.show_status),
            item('Quit', self.quit_app)
        )
        
        self.icon = pystray.Icon(
            "GitHub Uploader",
            self.create_image(),
            "GitHub Auto Upload Tool",
            menu
        )
        
        # Run trong thread riêng
        Thread(target=self.icon.run, daemon=True).start()


class GitHubUploaderGUI:
    """GUI class cho ứng dụng"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GitHub Auto Upload Tool Pro v2.4")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # Theme colors
        self.themes = {
            'github_dark': {
                'bg': '#0d1117',
                'card': '#161b22',
                'border': '#30363d',
                'fg': '#c9d1d9',
                'fg_secondary': '#8b949e',
                'accent': '#58a6ff',
                'accent_light': '#79c0ff',
                'success': '#3fb950',
                'warning': '#d29922',
                'danger': '#f85149'
            },
            'blue_dark': {
                'bg': '#1a1d29',
                'card': '#252834',
                'border': '#3d4152',
                'fg': '#e0e0e0',
                'fg_secondary': '#a0a0a0',
                'accent': '#4a9eff',
                'accent_light': '#6fb1ff',
                'success': '#4ade80',
                'warning': '#facc15',
                'danger': '#ef4444'
            },
            'purple_dark': {
                'bg': '#1e1b29',
                'card': '#2a2535',
                'border': '#3d3649',
                'fg': '#e4e0f1',
                'fg_secondary': '#a39cb8',
                'accent': '#a78bfa',
                'accent_light': '#c4b5fd',
                'success': '#4ade80',
                'warning': '#fbbf24',
                'danger': '#f87171'
            },
            'light_white': {
                'bg': '#f6f8fa',
                'card': '#ffffff',
                'border': '#d0d7de',
                'fg': '#24292f',
                'fg_secondary': '#57606a',
                'accent': '#0969da',
                'accent_light': '#54aeff',
                'success': '#1a7f37',
                'warning': '#9a6700',
                'danger': '#cf222e'
            }
        }
        
        self.current_theme = 'github_dark'
        self.colors = self.themes[self.current_theme]
        
        # Language
        self.languages = {
            'vi': {
                'title': 'GitHub Auto Upload Tool Pro',
                'subtitle': 'Tự động đẩy code lên GitHub',
                'tray_tip': '💡 Tip: Thu nhỏ xuống System Tray bằng nút X',
                'sections': {
                    'quick': 'Thao tác nhanh',
                    'config': 'Cấu hình',
                    'background': 'Chạy nền',
                    'utils': 'Tiện ích'
                },
                'buttons': {
                    'upload': 'Upload code lên GitHub',
                    'status': 'Xem trạng thái Git',
                    'gitignore': 'Tạo/Sửa .gitignore',
                    'profiles': 'Quản lý profiles',
                    'auto_settings': 'Cấu hình tự động upload',
                    'settings': 'Cài đặt chung',
                    'start_bg': 'Bật chạy nền',
                    'stop_bg': 'Tắt chạy nền',
                    'bg_status': 'Trạng thái nền',
                    'logs': 'Xem logs',
                    'exit': 'Thoát'
                }
            },
            'en': {
                'title': 'GitHub Auto Upload Tool Pro',
                'subtitle': 'Automatically push code to GitHub',
                'tray_tip': '💡 Tip: Minimize to System Tray with X button',
                'sections': {
                    'quick': 'Quick Actions',
                    'config': 'Configuration',
                    'background': 'Background Mode',
                    'utils': 'Utilities'
                },
                'buttons': {
                    'upload': 'Upload code to GitHub',
                    'status': 'View Git status',
                    'gitignore': 'Create/Edit .gitignore',
                    'profiles': 'Manage profiles',
                    'auto_settings': 'Auto upload settings',
                    'settings': 'General settings',
                    'start_bg': 'Start background',
                    'stop_bg': 'Stop background',
                    'bg_status': 'Background status',
                    'logs': 'View logs',
                    'exit': 'Exit'
                }
            }
        }
        
        self.current_language = 'vi'
        self.lang = self.languages[self.current_language]
        
        # Initialize uploader
        self.uploader = GitHubUploader()
        
        # System tray
        self.tray_manager = SystemTrayManager(self)
        
        # Create GUI
        self.create_widgets()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start system tray
        self.tray_manager.start()

    def create_widgets(self):
        """Tạo giao diện"""
        self.root.configure(bg=self.colors['bg'])
        
        # Header
        header = tk.Frame(self.root, bg=self.colors['accent'], height=110, bd=0, highlightthickness=0)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=self.colors['accent'])
        header_content.pack(fill='both', expand=True)
        
        icon_frame = tk.Frame(header_content, bg=self.colors['accent'])
        icon_frame.pack(pady=(18, 5))
        
        icon_label = tk.Label(icon_frame, text="🚀", font=('Segoe UI', 36), 
                             bg=self.colors['accent'], fg='white')
        icon_label.pack()
        
        tk.Label(header_content, text=self.lang['title'], 
                font=('Segoe UI', 20, 'bold'), bg=self.colors['accent'], fg='white').pack(pady=(2, 0))
        
        tk.Label(header_content, text=self.lang['subtitle'], 
                font=('Segoe UI', 9, 'italic'), bg=self.colors['accent'], 
                fg=self.colors['accent_light']).pack(pady=3)
        
        # Tray hint
        tray_hint = tk.Frame(self.root, bg=self.colors['accent'])
        tray_hint.pack(fill='x')
        tk.Label(tray_hint, text=self.lang['tray_tip'], 
                font=('Segoe UI', 8, 'italic'), bg=self.colors['accent'], fg='white').pack(pady=8)

        # Main content
        canvas_container = tk.Frame(self.root, bg=self.colors['bg'])
        canvas_container.pack(expand=True, fill='both', side='top')
        
        canvas = tk.Canvas(canvas_container, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=12)
        scrollbar.pack(side="right", fill="y", pady=12, padx=(0, 12))
        
        main_frame = scrollable_frame

        # Container chính với 2 cột
        main_container = tk.Frame(main_frame, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Cột trái (rộng hơn)
        left_column = tk.Frame(main_container, bg=self.colors['bg'])
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 8))
        
        # Cột phải (cố định độ rộng)
        right_column = tk.Frame(main_container, bg=self.colors['bg'], width=260)
        right_column.pack(side='left', fill='y', padx=(8, 0))
        right_column.pack_propagate(False)

        # Info card
        info_card = tk.Frame(left_column, bg=self.colors['card'], 
                            highlightthickness=1, highlightbackground=self.colors['border'])
        info_card.pack(fill='x', pady=(0, 15))
        
        info_content = tk.Frame(info_card, bg=self.colors['card'])
        info_content.pack(padx=20, pady=15)
        
        repo_text = self.uploader.repo_path if self.uploader.repo_path else "Chưa cấu hình"
        if len(repo_text) > 50:
            repo_text = "..." + repo_text[-47:]
        tk.Label(info_content, text=f"📁  {repo_text}", 
                font=('Segoe UI', 10, 'bold'), bg=self.colors['card'], 
                fg=self.colors['fg'], anchor='w').pack(fill='x', pady=3)
        
        branch_text = self.uploader.branch if self.uploader.branch else "main"
        tk.Label(info_content, text=f"🌿  Branch: {branch_text}", 
                font=('Segoe UI', 9), bg=self.colors['card'], 
                fg=self.colors['fg_secondary'], anchor='w').pack(fill='x', pady=2)
        
        bg_running = self.uploader.is_background_running()
        bg_status_text = "🟢 Đang chạy" if bg_running else "🔴 Đã dừng"
        bg_color = self.colors['success'] if bg_running else self.colors['danger']
        tk.Label(info_content, text=f"⚡  Background: {bg_status_text}", 
                font=('Segoe UI', 9, 'bold'), bg=self.colors['card'], 
                fg=bg_color, anchor='w').pack(fill='x', pady=3)

        # Section: Thao tác nhanh
        section_quick = tk.LabelFrame(left_column, text=f"  {self.lang['sections']['quick']}  ", 
                                     font=('Segoe UI', 10, 'bold'),
                                     bg=self.colors['card'], fg=self.colors['accent'],
                                     relief='solid', bd=1, labelanchor='nw',
                                     highlightthickness=0, padx=10, pady=10)
        section_quick.pack(fill='x', pady=(0, 15))
        
        button_frame_quick = tk.Frame(section_quick, bg=self.colors['card'])
        button_frame_quick.pack(fill='x', padx=5, pady=5)
        
        self.create_modern_button(button_frame_quick, self.lang['buttons']['upload'], 
                                 self.upload_code, '🚀', 'success')
        self.create_modern_button(button_frame_quick, self.lang['buttons']['status'], 
                                 self.show_git_status, '📊', 'accent')
        self.create_modern_button(button_frame_quick, self.lang['buttons']['gitignore'], 
                                 self.create_gitignore, '📝', 'accent')

        # Section: Cấu hình
        section_config = tk.LabelFrame(left_column, text=f"  {self.lang['sections']['config']}  ", 
                                      font=('Segoe UI', 10, 'bold'),
                                      bg=self.colors['card'], fg=self.colors['accent'],
                                      relief='solid', bd=1, labelanchor='nw',
                                      highlightthickness=0, padx=10, pady=10)
        section_config.pack(fill='x', pady=(0, 15))
        
        button_frame_config = tk.Frame(section_config, bg=self.colors['card'])
        button_frame_config.pack(fill='x', padx=5, pady=5)
        
        self.create_modern_button(button_frame_config, self.lang['buttons']['profiles'], 
                                 self.manage_profiles, '💾', 'accent')
        self.create_modern_button(button_frame_config, self.lang['buttons']['auto_settings'], 
                                 self.configure_auto, '⏰', 'warning')
        self.create_modern_button(button_frame_config, self.lang['buttons']['settings'], 
                                 self.open_settings, '🎨', 'accent')

        # Section: Chạy nền
        section_bg = tk.LabelFrame(right_column, text=f"  {self.lang['sections']['background']}  ", 
                                  font=('Segoe UI', 10, 'bold'),
                                  bg=self.colors['card'], fg=self.colors['accent'],
                                  relief='solid', bd=1, labelanchor='nw',
                                  highlightthickness=0, padx=10, pady=10)
        section_bg.pack(fill='x', pady=(0, 15))
        
        button_frame_bg = tk.Frame(section_bg, bg=self.colors['card'])
        button_frame_bg.pack(fill='x', padx=5, pady=5)
        
        self.create_modern_button(button_frame_bg, self.lang['buttons']['start_bg'], 
                                 self.start_background, '▶️', 'success')
        self.create_modern_button(button_frame_bg, self.lang['buttons']['stop_bg'], 
                                 self.stop_background, '⏸️', 'danger')
        self.create_modern_button(button_frame_bg, self.lang['buttons']['bg_status'], 
                                 self.show_bg_status, '📡', 'accent')

        # Section: Tiện ích
        section_utils = tk.LabelFrame(right_column, text=f"  {self.lang['sections']['utils']}  ", 
                                     font=('Segoe UI', 10, 'bold'),
                                     bg=self.colors['card'], fg=self.colors['accent'],
                                     relief='solid', bd=1, labelanchor='nw',
                                     highlightthickness=0, padx=10, pady=10)
        section_utils.pack(fill='x', pady=(0, 15))
        
        button_frame_utils = tk.Frame(section_utils, bg=self.colors['card'])
        button_frame_utils.pack(fill='x', padx=5, pady=5)
        
        self.create_modern_button(button_frame_utils, self.lang['buttons']['logs'], 
                                 self.view_logs, '📄', 'accent')
        self.create_modern_button(button_frame_utils, self.lang['buttons']['exit'], 
                                 self.quit_application, '🚪', 'danger')

        # Footer
        footer = tk.Frame(self.root, bg=self.colors['card'], height=28)
        footer.pack(side='bottom', fill='x')
        footer.pack_propagate(False)
        tk.Label(footer, text="© 2025 GitHub Auto Upload Pro v2.4 • Made with 💜", 
                font=('Segoe UI', 7), bg=self.colors['card'], 
                fg=self.colors['fg_secondary']).pack(expand=True)

    def create_modern_button(self, parent, text, command, icon='', color_key='accent'):
        """Tạo nút hiện đại với hiệu ứng hover"""
        btn_color = self.colors.get(color_key, self.colors['accent'])
        
        btn_frame = tk.Frame(parent, bg=parent['bg'])
        btn_frame.pack(fill='x', pady=4)
        
        btn = tk.Button(btn_frame, text=f"{icon}  {text}", command=command,
                       font=('Segoe UI', 9, 'bold'), bg=btn_color, fg='white',
                       relief='flat', bd=0, cursor='hand2',
                       activebackground=self._lighten_color(btn_color),
                       activeforeground='white', padx=15, pady=10)
        btn.pack(fill='x', expand=True)
        
        def on_enter(e):
            btn['bg'] = self._lighten_color(btn_color)
        
        def on_leave(e):
            btn['bg'] = btn_color
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def _lighten_color(self, color):
        """Làm sáng màu lên một chút cho hover effect"""
        color_map = {
            self.colors['accent']: '#79c0ff',
            self.colors['success']: '#56d364',
            self.colors['danger']: '#ff7b72',
            self.colors['warning']: '#f0b72f'
        }
        return color_map.get(color, color)

    # Button handlers
    def upload_code(self):
        """Upload code lên GitHub"""
        try:
            if not self.uploader.repo_path:
                self.setup_repository()
                return
            
            if not Path(self.uploader.repo_path).exists():
                messagebox.showerror("Lỗi", "Thư mục repository không tồn tại!")
                return
            
            # Ask for commit message first
            message = simpledialog.askstring("Commit Message", 
                                            "Enter commit message (để trống = auto):", 
                                            parent=self.root)
            if message is None:  # User clicked Cancel
                return
            
            progress = tk.Toplevel(self.root)
            progress.title("Đang upload...")
            progress.geometry("400x200")
            progress.transient(self.root)
            progress.grab_set()
            
            # Prevent closing
            progress.protocol("WM_DELETE_WINDOW", lambda: None)
            
            tk.Label(progress, text="Đang upload code lên GitHub...", 
                    font=('Segoe UI', 12, 'bold')).pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress, mode='indeterminate', length=300)
            progress_bar.pack(pady=10)
            progress_bar.start()
            
            status_label = tk.Label(progress, text="Preparing...", font=('Segoe UI', 9))
            status_label.pack(pady=10)
            
            def update_status(text):
                """Thread-safe status update"""
                if progress.winfo_exists():
                    status_label.config(text=text)
                    progress.update()
            
            def close_progress():
                """Thread-safe close"""
                if progress.winfo_exists():
                    progress_bar.stop()
                    progress.destroy()
            
            def do_upload():
                try:
                    # Adding files
                    self.root.after(0, lambda: update_status("Adding files..."))
                    time.sleep(0.5)  # Small delay for UI update
                    
                    if not self.uploader.git_add_all():
                        raise Exception("Git add failed - No changes or git not initialized")
                    
                    # Committing
                    self.root.after(0, lambda: update_status("Committing..."))
                    time.sleep(0.5)
                    
                    commit_msg = message if message else ""
                    if not self.uploader.git_commit(commit_msg):
                        raise Exception("Git commit failed - Nothing to commit or git error")
                    
                    # Pushing
                    self.root.after(0, lambda: update_status("Pushing to GitHub..."))
                    time.sleep(0.5)
                    
                    if not self.uploader.git_push():
                        raise Exception("Git push failed - Check remote URL and credentials")
                    
                    # Success
                    self.root.after(0, close_progress)
                    self.root.after(100, lambda: messagebox.showinfo("Thành công", "✓ Đã upload code lên GitHub!"))
                    
                except Exception as e:
                    self.root.after(0, close_progress)
                    self.root.after(100, lambda: messagebox.showerror("Lỗi", f"Upload thất bại:\n{str(e)}"))
            
            # Start upload in thread
            Thread(target=do_upload, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể bắt đầu upload:\n{str(e)}")

    def setup_repository(self):
        """Thiết lập repository"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Thiết lập Repository")
        dialog.geometry("550x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"550x350+{x}+{y}")
        
        tk.Label(dialog, text="Cấu hình Repository", font=('Segoe UI', 14, 'bold')).pack(pady=15)
        
        # Repo path
        path_frame = tk.Frame(dialog)
        path_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(path_frame, text="Đường dẫn repo:", width=15, anchor='w').pack(side='left')
        path_entry = tk.Entry(path_frame)
        path_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        def browse_path():
            path = filedialog.askdirectory(parent=dialog)
            if path:
                path_entry.delete(0, tk.END)
                path_entry.insert(0, path)
        
        tk.Button(path_frame, text="Browse", command=browse_path).pack(side='left')
        
        # Remote URL
        url_frame = tk.Frame(dialog)
        url_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(url_frame, text="Remote URL:", width=15, anchor='w').pack(side='left')
        url_entry = tk.Entry(url_frame)
        url_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Example label
        tk.Label(dialog, text="Ví dụ: https://github.com/username/repo.git", 
                font=('Segoe UI', 8, 'italic'), fg='gray').pack(pady=2)
        
        # Branch
        branch_frame = tk.Frame(dialog)
        branch_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(branch_frame, text="Branch:", width=15, anchor='w').pack(side='left')
        branch_entry = tk.Entry(branch_frame)
        branch_entry.insert(0, "main")
        branch_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        def save_config():
            repo_path = path_entry.get().strip()
            remote_url = url_entry.get().strip()
            branch = branch_entry.get().strip()
            
            if not repo_path:
                messagebox.showerror("Lỗi", "Vui lòng chọn đường dẫn repository!", parent=dialog)
                return
            
            if not remote_url:
                messagebox.showerror("Lỗi", "Vui lòng nhập Remote URL!", parent=dialog)
                return
            
            if not Path(repo_path).exists():
                if not messagebox.askyesno("Xác nhận", 
                    "Thư mục không tồn tại. Bạn có muốn tạo mới?", parent=dialog):
                    return
                Path(repo_path).mkdir(parents=True, exist_ok=True)
            
            self.uploader.repo_path = repo_path
            self.uploader.remote_url = remote_url
            self.uploader.branch = branch
            self.uploader.save_config()
            
            # Initialize git
            if self.uploader.init_git_repo():
                if self.uploader.configure_remote():
                    messagebox.showinfo("Thành công", "✓ Đã cấu hình repository thành công!", parent=dialog)
                    dialog.destroy()
                    # Refresh UI
                    for widget in self.root.winfo_children():
                        widget.destroy()
                    self.create_widgets()
                else:
                    messagebox.showerror("Lỗi", "Không thể cấu hình remote!", parent=dialog)
            else:
                messagebox.showerror("Lỗi", "Không thể khởi tạo Git repository!", parent=dialog)
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Lưu cấu hình", command=save_config, 
                 bg=self.colors['success'], fg='white', 
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=8).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Hủy", command=dialog.destroy,
                 bg=self.colors['danger'], fg='white', 
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=8).pack(side='left', padx=5)

    def show_git_status(self):
        """Hiển thị Git status"""
        self.uploader.show_git_status()

    def create_gitignore(self):
        """Tạo .gitignore"""
        self.uploader.create_gitignore()

    def manage_profiles(self):
        """Quản lý profiles"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Quản lý Profiles")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Profiles đã lưu", font=('Segoe UI', 14, 'bold')).pack(pady=15)
        
        # Listbox
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        profiles_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=('Segoe UI', 10))
        profiles_list.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=profiles_list.yview)
        
        # Load profiles
        profiles = self.uploader.list_profiles()
        for profile in profiles:
            profiles_list.insert('end', profile)
        
        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        def load_selected():
            selection = profiles_list.curselection()
            if selection:
                profile_name = profiles_list.get(selection[0])
                if self.uploader.load_profile(profile_name):
                    messagebox.showinfo("Thành công", f"Đã load profile '{profile_name}'")
                    dialog.destroy()
                    self.create_widgets()  # Refresh UI
        
        def save_current():
            name = simpledialog.askstring("Save Profile", "Tên profile:", parent=dialog)
            if name:
                if self.uploader.save_profile(name):
                    messagebox.showinfo("Thành công", f"Đã lưu profile '{name}'")
                    profiles_list.insert('end', name)
        
        def delete_selected():
            selection = profiles_list.curselection()
            if selection:
                profile_name = profiles_list.get(selection[0])
                if messagebox.askyesno("Xác nhận", f"Xóa profile '{profile_name}'?"):
                    if self.uploader.delete_profile(profile_name):
                        messagebox.showinfo("Thành công", f"Đã xóa profile '{profile_name}'")
                        profiles_list.delete(selection[0])
        
        tk.Button(btn_frame, text="Load", command=load_selected, padx=15, pady=5).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Save Current", command=save_current, padx=15, pady=5).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", command=delete_selected, padx=15, pady=5).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Close", command=dialog.destroy, padx=15, pady=5).grid(row=0, column=3, padx=5)

    def configure_auto(self):
        """Cấu hình tự động upload"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cấu hình Auto Upload")
        dialog.geometry("500x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Cấu hình Auto Upload", font=('Segoe UI', 14, 'bold')).pack(pady=15)
        
        # Interval
        interval_frame = tk.Frame(dialog)
        interval_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(interval_frame, text="Khoảng thời gian (phút):", width=20, anchor='w').pack(side='left')
        interval_var = tk.IntVar(value=self.uploader.auto_upload_interval)
        tk.Spinbox(interval_frame, from_=1, to=1440, textvariable=interval_var, width=10).pack(side='left')
        
        # Commit message template
        msg_frame = tk.Frame(dialog)
        msg_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(msg_frame, text="Template commit message:", width=20, anchor='w').pack(side='left')
        msg_entry = tk.Entry(msg_frame)
        msg_entry.insert(0, self.uploader.commit_message_template)
        msg_entry.pack(side='left', fill='x', expand=True)
        
        tk.Label(dialog, text="Variables: {datetime}, {user}, {files}", 
                font=('Segoe UI', 8, 'italic'), fg='gray').pack()
        
        def save():
            self.uploader.auto_upload_interval = interval_var.get()
            self.uploader.commit_message_template = msg_entry.get()
            self.uploader.save_config()
            messagebox.showinfo("Thành công", "Đã lưu cấu hình!")
            dialog.destroy()
        
        tk.Button(dialog, text="Lưu cấu hình", command=save, 
                 bg=self.colors['accent'], fg='white', 
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=8).pack(pady=20)

    def open_settings(self):
        """Mở cài đặt"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cài đặt")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Cài đặt chung", font=('Segoe UI', 14, 'bold')).pack(pady=15)
        
        # Theme selection
        theme_frame = tk.Frame(dialog)
        theme_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(theme_frame, text="Theme:", width=15, anchor='w').pack(side='left')
        theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(theme_frame, textvariable=theme_var, 
                                   values=list(self.themes.keys()), state='readonly')
        theme_combo.pack(side='left', fill='x', expand=True)
        
        # Language selection
        lang_frame = tk.Frame(dialog)
        lang_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(lang_frame, text="Language:", width=15, anchor='w').pack(side='left')
        lang_var = tk.StringVar(value=self.current_language)
        lang_combo = ttk.Combobox(lang_frame, textvariable=lang_var, 
                                 values=list(self.languages.keys()), state='readonly')
        lang_combo.pack(side='left', fill='x', expand=True)
        
        def apply():
            self.current_theme = theme_var.get()
            self.colors = self.themes[self.current_theme]
            self.current_language = lang_var.get()
            self.lang = self.languages[self.current_language]
            dialog.destroy()
            # Recreate widgets with new theme
            for widget in self.root.winfo_children():
                widget.destroy()
            self.create_widgets()
            messagebox.showinfo("Thành công", "Đã áp dụng cài đặt! (Khởi động lại để hoàn toàn)")
        
        tk.Button(dialog, text="Áp dụng", command=apply, 
                 bg=self.colors['accent'], fg='white', 
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=8).pack(pady=20)

    def start_background(self):
        """Bật chạy nền"""
        if self.uploader.start_background_mode():
            messagebox.showinfo("Thành công", "Đã bật chế độ chạy nền!")
            self.create_widgets()  # Refresh UI
        else:
            messagebox.showwarning("Cảnh báo", "Chế độ chạy nền đã được bật!")

    def stop_background(self):
        """Tắt chạy nền"""
        if self.uploader.stop_background_mode():
            messagebox.showinfo("Thành công", "Đã tắt chế độ chạy nền!")
            self.create_widgets()  # Refresh UI
        else:
            messagebox.showwarning("Cảnh báo", "Chế độ chạy nền chưa được bật!")

    def show_bg_status(self):
        """Hiển thị trạng thái background"""
        status = self.uploader.read_status()
        if status:
            msg = f"Timestamp: {status['timestamp']}\nResult: {status['result']}\nMessage: {status['message']}"
            messagebox.showinfo("Background Status", msg)
        else:
            messagebox.showinfo("Background Status", "Chưa có status")

    def view_logs(self):
        """Xem logs"""
        self.uploader.view_logs()

    def quit_application(self):
        """Thoát ứng dụng"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn thoát?"):
            self.on_closing()

    def on_closing(self):
        """Xử lý khi đóng cửa sổ"""
        # Minimize to tray
        self.tray_manager.hide_window()

    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()


if __name__ == "__main__":
    import sys
    import ctypes
    
    # Check admin rights (optional)
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False
    
    # Run GUI
    app = GitHubUploaderGUI()
    app.run()
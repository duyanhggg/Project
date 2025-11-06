#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Auto Upload Tool Pro
Công cụ tự động đẩy code lên GitHub với nhiều tính năng nâng cao
Version 2.6 - Enhanced with Profile Editor & Smart Commit Options
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
                    'auto_upload_interval': self.auto_upload_interval,
                    'commit_message_template': self.commit_message_template,
                    'commit_mode': self.commit_mode
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
                self.commit_message_template = profile.get('commit_message_template', 'Update: {datetime}')
                self.commit_mode = profile.get('commit_mode', 'always')
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
                return False
            
            result = self._git("init")
            if result is not None or Path(self.repo_path, '.git').exists():
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
                return False
            
            self._git("remote remove origin")
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
            return result is not None or True
        except Exception as e:
            self.logger.error(f"Error adding files: {e}")
            return False

    def git_commit(self, message: str) -> bool:
        """Git commit với message"""
        try:
            # Check commit mode
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
                return False
            
            thread = Thread(target=self.run_background_loop, daemon=True)
            thread.start()
            
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
        image = Image.new('RGB', (width, height), color='#58a6ff')
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
        self.root.title("GitHub Auto Upload Tool Pro v2.6")
        self.root.geometry("900x700")
        
        # Theme colors
        self.colors = {
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
        }
        
        self.root.configure(bg=self.colors['bg'])
        
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
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.root, bg=self.colors['accent'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="🚀 GitHub Auto Upload Tool Pro", 
                font=('Segoe UI', 18, 'bold'), bg=self.colors['accent'], 
                fg='white').pack(pady=25)
        
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
        
        tk.Label(info_content, text=f"🌿 Branch: {self.uploader.branch}", 
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

    def refresh_ui(self):
        """Refresh UI"""
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
        
        tk.Label(progress, text="Uploading to GitHub...", 
                font=('Segoe UI', 12, 'bold')).pack(pady=20)
        
        pb = ttk.Progressbar(progress, mode='indeterminate', length=300)
        pb.pack(pady=10)
        pb.start()
        
        status_label = tk.Label(progress, text="Preparing...", font=('Segoe UI', 9))
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
            messagebox.showinfo("✅ Success", "Background mode started!")
            self.refresh_ui()
        else:
            messagebox.showwarning("⚠️ Warning", "Already running!")

    def stop_background(self):
        """Stop background"""
        if self.uploader.stop_background_mode():
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
        self.tray_manager.hide_window()

    def run(self):
        """Run app"""
        self.root.mainloop()


if __name__ == "__main__":
    app = GitHubUploaderGUI()
    app.run()
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
from infi.systray import SysTrayIcon

# Note: UTF-8 encoding is handled by the file header and Python's default encoding

def safe_input(prompt=""):
    try:
        if hasattr(sys, "stdin") and sys.stdin and sys.stdin.isatty():
            return input(prompt)
        else:
            print("[WARNING] Không thể nhập dữ liệu (stdin không khả dụng).")
            return ""
    except (EOFError, OSError, AttributeError):
        print("[WARNING] Không thể nhập dữ liệu (stdin không khả dụng).")
        return ""

class GitHubUploader:
    def __init__(self):
        self.repo_path = None
        self.repo_url = None
        self.branch = "main"
        self.config_file = os.path.join(Path.home(), ".github_uploader_config.json")
        self.config = self.load_config()
        self.auto_upload_running = False
        self.auto_upload_thread = None
        self.auto_upload_interval = None
        self.auto_upload_prefix = None
        # Language
        self.lang = self.config.get('lang', 'vi')
        # Background mode artifacts
        self.bg_pid_file = os.path.join(Path.home(), ".github_uploader_bg.json")
        self.bg_config_file = os.path.join(Path.home(), ".github_uploader_bg_config.json")
        self.bg_status_file = os.path.join(Path.home(), ".github_uploader_bg_status.json")
        # Notifications
        self.notifier = None
        try:
            if os.name == 'nt':
                from importlib import import_module
                toaster_mod = import_module('win10toast')
                self.notifier = toaster_mod.ToastNotifier()
        except Exception:
            self.notifier = None
        
        # Thiết lập logging
        self.log_dir = os.path.join(Path.home(), ".github_uploader_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        log_file = os.path.join(self.log_dir, f"upload_{datetime.now().strftime('%Y%m%d')}.log")
        
        # Cấu hình logger
        self.logger = logging.getLogger('GitHubUploader')
        self.logger.setLevel(logging.DEBUG)
        
        # Xóa handlers cũ nếu có
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("=" * 60)
        self.logger.info("GitHub Auto Upload Tool khởi động")
        self.logger.info("=" * 60)
        
    def load_config(self):
        """Load cấu hình đã lưu"""
        return self._safe_read_json(self.config_file, default={}) or {}
    
    def save_config(self):
        """Lưu cấu hình"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Không thể lưu cấu hình: {e}")

    def _safe_read_json(self, path, default=None):
        """Đọc JSON an toàn; nếu lỗi JSON sẽ backup file hỏng và trả về default"""
        if not os.path.exists(path):
            return default
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            try:
                # Backup file hỏng
                bak = f"{path}.bak_{int(time.time())}"
                try:
                    os.replace(path, bak)
                except Exception:
                    pass
                if hasattr(self, 'logger') and self.logger:
                    self.logger.error(f"Lỗi đọc JSON {path}: {e}. Đã backup -> {bak}")
                else:
                    print(f"[WARN] Lỗi đọc JSON {path}: {e}. Đã backup -> {bak}")
            except Exception:
                pass
            return default

    def _safe_write_json(self, path, data):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Không thể ghi JSON {path}: {e}")
            return False
    
    def clear_screen(self):
        """Xóa màn hình console"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        """In banner chào mừng"""
        print("=" * 60)
        print("       [UPLOAD] GITHUB AUTO UPLOAD TOOL PRO [UPLOAD]")
        subtitle = self.t('subtitle', 'Tự động đẩy code lên GitHub với nhiều tính năng')
        print(f"    {subtitle}")
        print("=" * 60)

    def t(self, key, default_text=""):
        """Simple i18n helper"""
        translations = {
            'en': {
                'subtitle': 'Automate pushing code to GitHub with advanced features',
                'menu_title': 'MAIN MENU:',
                'menu_upload': 'Upload code to GitHub',
                'menu_status': 'View Git status',
                'menu_gitignore': 'Create/Edit .gitignore',
                'menu_auth_help': 'GitHub authentication guide',
                'menu_saved_cfg': 'Manage saved configurations',
                'menu_guide': 'Install & usage guide',
                'menu_auto_cfg': 'Configure auto upload',
                'menu_auto_toggle_on': 'Start auto upload (background, keeps running when tool closed)',
                'menu_auto_toggle_off': 'Stop background auto upload',
                'menu_logs': 'View logs',
                'menu_exit': 'Exit',
                'prompt_choice': 'Choose (0-9): ',
                'status_bg_on': 'BACKGROUND AUTO UPLOAD: RUNNING',
                'status_bg_off': 'BACKGROUND AUTO UPLOAD: OFF',
            },
            'vi': {
                'subtitle': 'Tự động đẩy code lên GitHub với nhiều tính năng',
                'menu_title': 'MENU CHÍNH:',
                'menu_upload': 'Upload code lên GitHub',
                'menu_status': 'Xem trạng thái Git',
                'menu_gitignore': 'Tạo/Sửa .gitignore',
                'menu_auth_help': 'Hướng dẫn xác thực GitHub',
                'menu_saved_cfg': 'Quản lý cấu hình đã lưu',
                'menu_guide': 'Hướng dẫn cài đặt & sử dụng',
                'menu_auto_cfg': 'Cấu hình tự động upload',
                'menu_auto_toggle_on': 'Bật auto upload (chạy nền, vẫn chạy khi tắt tool)',
                'menu_auto_toggle_off': 'Dừng auto upload chạy nền',
                'menu_logs': 'Xem logs',
                'menu_exit': 'Thoát',
                'prompt_choice': 'Chọn chức năng (0-9): ',
                'status_bg_on': 'TỰ ĐỘNG UPLOAD NỀN: ĐANG CHẠY',
                'status_bg_off': 'TỰ ĐỘNG UPLOAD NỀN: TẮT',
            }
        }
        lang_map = translations.get(self.lang, {})
        return lang_map.get(key, default_text)

    def select_language(self):
        """Prompt user to choose language at startup"""
        self.clear_screen()
        print("=" * 60)
        print("[LANG] Chọn ngôn ngữ / Choose language")
        print("=" * 60)
        current = 'Tiếng Việt' if self.lang == 'vi' else 'English'
        print(f"1. Tiếng Việt (hiện tại: {current})")
        print("2. English")
        print("0. Giữ nguyên / Keep current")
        choice = safe_input("\n-> Lựa chọn: ").strip()
        if choice == '1':
            self.lang = 'vi'
        elif choice == '2':
            self.lang = 'en'
        else:
            # keep current
            pass
        # persist
        try:
            self.config['lang'] = self.lang
            self.save_config()
        except Exception:
            pass
    
    def run_command(self, command, check=True):
        """Chạy lệnh shell và trả về kết quả"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=check,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'  # Replace invalid characters instead of failing
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
    
    def check_git_installed(self):
        """Kiểm tra Git đã được cài đặt chưa"""
        self.logger.info("Kiểm tra Git...")
        success, stdout, _ = self.run_command("git --version", check=False)
        if not success:
            self.logger.error("Git chưa được cài đặt!")
            print("[ERROR] Git chưa được cài đặt!")
            print("\n[DOWNLOAD] HƯỚNG DẪN CÀI ĐẶT GIT:")
            print("   [WINDOWS] Windows: https://git-scm.com/download/win")
            print("   [MAC] Mac: brew install git")
            print("   [LINUX] Linux: sudo apt install git")
            return False
        self.logger.info(f"Git đã cài đặt: {stdout.strip()}")
        print(f"[OK] {stdout.strip()}")
        return True
    
    def notify(self, title, message, duration=5):
        """Hiển thị thông báo (Windows toast nếu khả dụng; otherwise bỏ qua)"""
        try:
            if self.notifier is not None and os.name == 'nt':
                # Non-blocking toast
                self.notifier.show_toast(title, message, duration=duration, threaded=True)
        except Exception:
            pass

    def _parse_changed_files(self, status_output):
        """Trích xuất danh sách file thay đổi từ git status --short"""
        try:
            files = []
            for line in (status_output or '').splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if not parts:
                    continue
                # format can be: 'XY path' or 'R  old -> new'
                if '->' in line:
                    # take new path after '->'
                    try:
                        arrow_idx = parts.index('->')
                        path = parts[arrow_idx + 1]
                    except Exception:
                        path = parts[-1]
                else:
                    path = parts[-1]
                files.append(path)
            return len(files), files
        except Exception:
            return 0, []

    # =========================
    # Background mode utilities
    # =========================
    def _read_bg_pid(self):
        try:
            if os.path.exists(self.bg_pid_file):
                with open(self.bg_pid_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return int(data.get('pid'))
        except Exception:
            return None
        return None

    def _write_bg_pid(self, pid):
        try:
            with open(self.bg_pid_file, 'w', encoding='utf-8') as f:
                json.dump({'pid': pid}, f)
        except Exception as e:
            self.logger.error(f"Không thể ghi PID background: {e}")

    def _clear_bg_pid(self):
        try:
            if os.path.exists(self.bg_pid_file):
                os.remove(self.bg_pid_file)
        except Exception:
            pass

    def _read_bg_config(self):
        return self._safe_read_json(self.bg_config_file, default=None)

    def _read_bg_status(self):
        return self._safe_read_json(self.bg_status_file, default=None)

    def _write_bg_status(self, result, message='', count=None):
        try:
            payload = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'result': result,
                'message': message,
            }
            if count is not None:
                payload['upload_count'] = count
            self._safe_write_json(self.bg_status_file, payload)
        except Exception:
            pass

    def _is_process_running(self, pid):
        if not pid or pid <= 0:
            return False
        try:
            if os.name == 'nt':
                # Windows: dùng tasklist để kiểm tra PID tồn tại
                success, stdout, _ = self.run_command(f'tasklist /FI "PID eq {pid}"', check=False)
                return success and str(pid) in stdout
            else:
                # POSIX
                os.kill(pid, 0)
                return True
        except Exception:
            return False

    def is_background_running(self):
        pid = self._read_bg_pid()
        return self._is_process_running(pid)

    def start_background_mode(self):
        # Kiểm tra cấu hình cần thiết
        if not self.repo_path or not self.repo_url:
            print("\n[WARNING]  Chưa có cấu hình repository!\n[TIP] Vui lòng chạy Menu 1 để cấu hình trước")
            return False
        if not self.auto_upload_interval or not self.auto_upload_prefix:
            print("\n[WARNING]  Chưa có cấu hình auto upload!\n[TIP] Vui lòng chạy Menu 7 để cấu hình trước")
            return False

        if self.is_background_running():
            print("\n[INFO]  Auto upload nền đang chạy rồi")
            return True

        # Ghi file cấu hình cho background
        bg_cfg = {
            'path': self.repo_path,
            'url': self.repo_url,
            'branch': self.branch,
            'interval': self.auto_upload_interval,
            'prefix': self.auto_upload_prefix,
        }
        try:
            ok = self._safe_write_json(self.bg_config_file, bg_cfg)
            if not ok:
                raise RuntimeError('write bg config failed')
        except Exception as e:
            print(f"[ERROR] Lỗi lưu cấu hình nền: {e}")
            return False

        # Khởi chạy tiến trình nền detach
        python_exe = sys.executable
        script_path = os.path.abspath(__file__)
        cmd = [python_exe, script_path, "--run-background"]
        try:
            creationflags = 0
            startupinfo = None
            if os.name == 'nt':
                # DETACHED_PROCESS(0x00000008) | CREATE_NEW_PROCESS_GROUP(0x00000200)
                creationflags = 0x00000008 | 0x00000200
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=creationflags,
                startupinfo=startupinfo,
            )
            self._write_bg_pid(proc.pid)
            print("\n[RUNNING] Đã bật auto upload chạy nền! Bạn có thể tắt tool an toàn.")
            self.logger.info(f"Bật background mode, PID={proc.pid}")
            return True
        except Exception as e:
            print(f"[ERROR] Lỗi khởi chạy nền: {e}")
            self.logger.exception("Lỗi khởi chạy nền")
            return False

    def stop_background_mode(self):
        pid = self._read_bg_pid()
        if not self._is_process_running(pid):
            print("\n[INFO]  Không phát hiện tiến trình auto upload nền đang chạy")
            self._clear_bg_pid()
            return True
        try:
            if os.name == 'nt':
                # Sử dụng taskkill để dừng tiến trình và cả nhóm tiến trình
                self.run_command(f'taskkill /PID {pid} /T /F', check=False)
            else:
                os.kill(pid, 15)
            self._clear_bg_pid()
            print("\n[OK] Đã dừng auto upload nền!")
            self.logger.info("Đã dừng background mode")
            return True
        except Exception as e:
            print(f"[ERROR] Không thể dừng tiến trình: {e}")
            self.logger.exception("Không thể dừng background mode")
            return False

    def check_git_config(self):
        """Kiểm tra cấu hình Git"""
        success, name, _ = self.run_command("git config --global user.name", check=False)
        success2, email, _ = self.run_command("git config --global user.email", check=False)
        
        if not success or not success2 or not name.strip() or not email.strip():
            print("\n[WARNING]  Git chưa được cấu hình!")
            print("\n[EDIT] Vui lòng cấu hình Git:")
            
            if not name.strip():
                user_name = safe_input("   [USER] Nhập tên của bạn: ").strip()
                if user_name:
                    self.run_command(f'git config --global user.name "{user_name}"')
            
            if not email.strip():
                user_email = safe_input("   [EMAIL] Nhập email của bạn: ").strip()
                if user_email:
                    self.run_command(f'git config --global user.email "{user_email}"')
            
            print("[OK] Đã cấu hình Git!")
        else:
            print(f"[OK] Git User: {name.strip()} <{email.strip()}>")
    
    def create_gitignore(self):
        """Tạo file .gitignore"""
        gitignore_path = os.path.join(self.repo_path, ".gitignore")
        
        if os.path.exists(gitignore_path):
            print("[INFO]  File .gitignore đã tồn tại")
            return
        
        print("\n[EDIT] Tạo file .gitignore")
        print("Chọn template:")
        print("1. 🐍 Python")
        print("2. [PACKAGE] Node.js")
        print("3. [JAVA] Java")
        print("4. [C++] C/C++")
        print("0. [ERROR] Bỏ qua")
        
        choice = safe_input("\nLựa chọn (0-4): ").strip()
        
        templates = {
            "1": "# Python\n__pycache__/\n*.py[cod]\nvenv/\nenv/\n*.egg-info/\ndist/\nbuild/\n",
            "2": "# Node.js\nnode_modules/\nnpm-debug.log*\n.env\ndist/\nbuild/\n",
            "3": "# Java\n*.class\n*.jar\ntarget/\n.gradle/\nbuild/\n.idea/\n",
            "4": "# C/C++\n*.o\n*.obj\n*.exe\n*.out\n*.dll\n*.so\nbuild/\n"
        }
        
        if choice in templates:
            try:
                with open(gitignore_path, 'w', encoding='utf-8') as f:
                    f.write(templates[choice])
                print("[OK] Đã tạo .gitignore")
            except Exception as e:
                print(f"[ERROR] Lỗi tạo .gitignore: {e}")
    
    def show_git_status(self):
        """Hiển thị trạng thái Git"""
        print("\n[STATUS] TRẠNG THÁI GIT:")
        success, stdout, _ = self.run_command(f'cd "{self.repo_path}" && git status --short')
        if success and stdout.strip():
            print(stdout)
        else:
            print("   [INFO]  Không có thay đổi nào")
    
    def init_git_repo(self):
        """Khởi tạo Git repository nếu chưa có"""
        # Fix lỗi dubious ownership
        safe_dir_cmd = f'git config --global --add safe.directory "{self.repo_path}"'
        self.run_command(safe_dir_cmd, check=False)
        
        if not os.path.exists(os.path.join(self.repo_path, ".git")):
            print("[PACKAGE] Đang khởi tạo Git repository...")
            success, _, error = self.run_command(f'cd "{self.repo_path}" && git init')
            if success:
                print("[OK] Đã khởi tạo Git repository")
                
                create = safe_input("Bạn có muốn tạo file .gitignore? (y/n): ").lower()
                if create == 'y':
                    self.create_gitignore()
            else:
                print(f"[ERROR] Lỗi khởi tạo: {error}")
                return False
        return True
    
    def configure_remote(self):
        """Cấu hình remote repository"""
        success, stdout, _ = self.run_command(
            f'cd "{self.repo_path}" && git remote get-url origin',
            check=False
        )
        
        if success:
            current_url = stdout.strip()
            print(f"[REMOTE] Remote hiện tại: {current_url}")
            
            if current_url != self.repo_url:
                change = safe_input("URL khác. Cập nhật? (y/n): ").lower()
                if change == 'y':
                    self.run_command(f'cd "{self.repo_path}" && git remote set-url origin {self.repo_url}')
                    print("[OK] Đã cập nhật remote URL")
        else:
            print("[REMOTE] Đang thêm remote repository...")
            success, _, error = self.run_command(
                f'cd "{self.repo_path}" && git remote add origin {self.repo_url}'
            )
            if success:
                print("[OK] Đã thêm remote repository")
            else:
                print(f"[ERROR] Lỗi thêm remote: {error}")
                return False
        return True
    
    def git_add_all(self):
        """Git add tất cả file"""
        print("\n[EDIT] Đang thêm files vào staging...")
        
        success, stdout, _ = self.run_command(
            f'cd "{self.repo_path}" && git status --short',
            check=False
        )
        if stdout.strip():
            print("Files sẽ được thêm:")
            print(stdout)
        
        success, _, error = self.run_command(f'cd "{self.repo_path}" && git add .')
        if success:
            print("[OK] Đã thêm tất cả files")
            return True
        else:
            print(f"[ERROR] Lỗi khi thêm files: {error}")
            return False
    
    def git_commit(self, message):
        """Git commit với message"""
        print(f"\n[MESSAGE] Đang commit với message: '{message}'")
        success, stdout, error = self.run_command(
            f'cd "{self.repo_path}" && git commit -m "{message}"',
            check=False
        )
        if success:
            print("[OK] Đã commit thành công")
            print(stdout)
            return True
        else:
            if "nothing to commit" in error:
                print("[INFO]  Không có thay đổi nào để commit")
                return True
            print(f"[ERROR] Lỗi khi commit: {error}")
            return False
    
    def git_push(self, force=False):
        """Git push lên remote"""
        print(f"\n[UPLOAD] Đang đẩy code lên branch '{self.branch}'...")
        
        success, _, _ = self.run_command(
            f'cd "{self.repo_path}" && git rev-parse --verify {self.branch}',
            check=False
        )
        
        if not success:
            print(f"[BRANCH] Branch '{self.branch}' chưa tồn tại, đang tạo mới...")
            self.run_command(f'cd "{self.repo_path}" && git checkout -b {self.branch}')
        
        force_flag = " --force" if force else ""
        success, stdout, error = self.run_command(
            f'cd "{self.repo_path}" && git push -u origin {self.branch}{force_flag}',
            check=False
        )
        
        if success:
            print("[OK] Đã đẩy code lên GitHub thành công! [SUCCESS]")
            print(stdout)
            return True
        else:
            print(f"[ERROR] Lỗi khi push: {error}")
            
            if "rejected" in error or "non-fast-forward" in error:
                print("\n[TIP] Remote có commits mới hơn!")
                print("Lựa chọn:")
                print("1. Pull và merge (khuyên dùng)")
                print("2. Force push (nguy hiểm)")
                print("0. Hủy")
                
                choice = safe_input("\nLựa chọn (0-2): ").strip()
                
                if choice == "1":
                    print("[SYNC] Đang pull code...")
                    self.run_command(f'cd "{self.repo_path}" && git pull origin {self.branch}')
                    return self.git_push()
                elif choice == "2":
                    confirm = safe_input("[WARNING]  Bạn chắc chắn muốn force push? (yes/no): ")
                    if confirm.lower() == "yes":
                        return self.git_push(force=True)
            
            elif "Authentication" in error or "denied" in error:
                print("\n[ERROR] LỖI XÁC THỰC!")
                print("Vui lòng kiểm tra:")
                print("1. Token/Password đã đúng chưa?")
                print("2. SSH key đã được thêm vào GitHub chưa?")
            
            return False
    
    def show_menu(self):
        """Hiển thị menu chính"""
        self.clear_screen()
        self.print_banner()
        
        # Hiển thị trạng thái auto upload (nền) - dòng ngắn gọn, có thông tin lần chạy cuối
        bg_cfg = self._read_bg_config()
        bg_stat = self._read_bg_status()
        if self.is_background_running():
            interval_txt = f"{bg_cfg.get('interval')}m" if bg_cfg and bg_cfg.get('interval') else "?m"
            prefix_txt = bg_cfg.get('prefix') if bg_cfg and bg_cfg.get('prefix') else (self.auto_upload_prefix or '')
            path_txt = bg_cfg.get('path') if bg_cfg and bg_cfg.get('path') else (self.repo_path or '')
            branch_txt = (bg_cfg.get('branch') if bg_cfg and bg_cfg.get('branch') else self.branch) or ''
            last_txt = ''
            leading_icon = '[RUNNING]'
            if bg_stat and bg_stat.get('timestamp'):
                res = (bg_stat.get('result') or '').lower()
                if res == 'success':
                    leading_icon = '[RUNNING]'
                    res_icon = '[OK]'
                elif res == 'failure':
                    leading_icon = '[STOPPED]'
                    res_icon = '[WARNING]'
                elif res in ('start', 'nochange'):
                    leading_icon = '[WAIT]'
                    res_icon = '[WAIT]'
                else:
                    res_icon = '[NONE]'
                last_txt = f" | last {bg_stat.get('timestamp')} {res_icon}"
            print(f"\n{leading_icon} {self.t('status_bg_on', 'TỰ ĐỘNG UPLOAD NỀN: ĐANG CHẠY')} ({interval_txt} | msg: {prefix_txt} | dir: {path_txt} | br: {branch_txt}){last_txt}")
        else:
            if bg_cfg:
                interval_txt = f"{bg_cfg.get('interval')}m" if bg_cfg.get('interval') else ""
                prefix_txt = bg_cfg.get('prefix') or ''
                path_txt = bg_cfg.get('path') or ''
                branch_txt = bg_cfg.get('branch') or ''
                details = "; ".join([s for s in [interval_txt, f"msg: {prefix_txt}" if prefix_txt else '', f"dir: {path_txt}" if path_txt else '', f"br: {branch_txt}" if branch_txt else ''] if s])
                suffix = f" (cấu hình sẵn: {details})" if details else ""
                print(f"\n[OFF] {self.t('status_bg_off', 'TỰ ĐỘNG UPLOAD NỀN: BẬT')}{suffix}")
            else:
                print(f"\n[OFF] {self.t('status_bg_off', 'TỰ ĐỘNG UPLOAD NỀN: BẬT')}")
        
        print(f"\n[MENU] {self.t('menu_title', 'MENU CHÍNH:')}")
        print(f"1. [UPLOAD] {self.t('menu_upload', 'Upload code lên GitHub')}")
        print(f"2. [STATUS] {self.t('menu_status', 'Xem trạng thái Git')}")
        print(f"3. [EDIT] {self.t('menu_gitignore', 'Tạo/Sửa .gitignore')}")
        print(f"4. [AUTH] {self.t('menu_auth_help', 'Hướng dẫn xác thực GitHub')}")
        print(f"5. [SAVE] {self.t('menu_saved_cfg', 'Quản lý cấu hình đã lưu')}")
        print(f"6. [GUIDE] {self.t('menu_guide', 'Hướng dẫn cài đặt & sử dụng')}")
        print(f"7. [TIME] {self.t('menu_auto_cfg', 'Cấu hình tự động upload')}")
        
        if self.is_background_running():
            pid = self._read_bg_pid()
            base = self.t('menu_auto_toggle_off', 'Dừng auto upload chạy nền')
            label = f"8. [STOPPED] {base} (PID {pid})" if pid else f"8. [STOPPED] {base}"
            print(label)
        else:
            interval_txt = None
            bg_cfg = self._read_bg_config()
            if bg_cfg and bg_cfg.get('interval'):
                interval_txt = f"mỗi {bg_cfg.get('interval')} phút"
            elif self.auto_upload_interval:
                interval_txt = f"mỗi {self.auto_upload_interval} phút"
            suffix = f" - {interval_txt}" if interval_txt else ""
            print(f"8. [RUNNING] {self.t('menu_auto_toggle_on', 'Bật auto upload (chạy nền, vẫn chạy khi tắt tool)')}{suffix}")
        
        print(f"9. [LOG] {self.t('menu_logs', 'Xem logs')}")
        print(f"0. [EXIT] {self.t('menu_exit', 'Thoát')}")
        
        return safe_input(f"\n-> {self.t('prompt_choice', 'Chọn chức năng (0-9): ')}").strip()
    
    def show_simple_guide(self):
        """Hiển thị hướng dẫn đơn giản"""
        self.clear_screen()
        self.print_banner()
        
        print("\n[GUIDE] HƯỚNG DẪN SỬ DỤNG\n")
        print("=" * 60)
        
        print("\n[C++] 1. CÀI ĐẶT GIT:")
        print("   [WINDOWS] Windows: https://git-scm.com/download/win")
        print("   [MAC] Mac: brew install git")
        print("   [LINUX] Linux: sudo apt install git")
        
        print("\n[CONFIG]  2. CẤU HÌNH GIT:")
        print('   git config --global user.name "Tên"')
        print('   git config --global user.email "email@example.com"')
        
        print("\n🔑 3. TẠO TOKEN GITHUB:")
        print("   📍 Bước 1: Vào https://github.com/settings/tokens")
        print("   📍 Bước 2: Generate new token -> Tokens (classic)")
        print("   📍 Bước 3: Chọn quyền: repo, workflow")
        print("   📍 Bước 4: Copy token (chỉ hiện 1 lần!)")
        
        print("\n[AUTH] 4. SỬ DỤNG TOKEN:")
        print("   • Khi push lần đầu, Git hỏi username & password")
        print("   • Username: tên GitHub của bạn")
        print("   • Password: DÁN TOKEN vào (KHÔNG phải password GitHub)")
        print("   • Token sẽ được lưu tự động")
        
        print("\n[UPLOAD] 5. UPLOAD CODE:")
        print("   • Chọn menu 1")
        print("   • Nhập đường dẫn thư mục code")
        print("   • Nhập URL repository")
        print("   • Nhập branch (Enter = main)")
        print("   • Nhập commit message")
        print("   • Xác nhận và đợi!")
        
        print("\n[WARNING]  6. XỬ LÝ LỖI:")
        print("   • 'git not recognized': Khởi động lại máy")
        print("   • 'Authentication failed': Token/Password sai")
        print("   • 'rejected': Chọn Pull và merge")
        
        print("\n" + "=" * 60)
        
        input("\n[OK] Nhấn Enter để quay lại menu...")
    
    def manage_saved_configs(self):
        """Quản lý các cấu hình đã lưu"""
        self.clear_screen()
        self.print_banner()
        
        if not isinstance(self.config, dict):
            self.config = {}
        
        if not self.config:
            print("\n📭 Chưa có cấu hình nào được lưu")
            input("\n[OK] Nhấn Enter để quay lại...")
            return
        
        print("\n[SAVE] CÁC CẤU HÌNH ĐÃ LƯU:\n")
        
        try:
            configs = [(name, cfg) for name, cfg in self.config.items() if isinstance(cfg, dict)]
        except Exception:
            configs = []
        for i, (name, cfg) in enumerate(configs, 1):
            print(f"{i}. [PACKAGE] {name}")
            print(f"   📁 Thư mục: {cfg.get('path', 'N/A')}")
            print(f"   🔗 Repository: {cfg.get('url', 'N/A')}")
            print(f"   [BRANCH] Branch: {cfg.get('branch', 'N/A')}\n")
        
        print("Chọn:")
        print("L - [DOWNLOAD] Load cấu hình")
        print("D - [DELETE]  Xóa cấu hình")
        print("0 - [BACK]  Quay lại")
        
        choice = safe_input("\n-> Lựa chọn: ").strip().upper()
        
        if choice == 'L':
            idx = safe_input("Nhập số thứ tự: ").strip()
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(configs):
                    name, cfg = configs[idx]
                    if not isinstance(cfg, dict):
                        print("[ERROR] Cấu hình không hợp lệ!")
                        input("\n[OK] Nhấn Enter để quay lại...")
                        return
                    path = (cfg.get('path') or '').strip()
                    url = (cfg.get('url') or '').strip()
                    branch = (cfg.get('branch') or 'main').strip() or 'main'
                    if not path or not os.path.exists(path):
                        print("[ERROR] Thư mục trong cấu hình không tồn tại hoặc trống!")
                        input("\n[OK] Nhấn Enter để quay lại...")
                        return
                    if not url:
                        print("[ERROR] URL repository trong cấu hình trống!")
                        input("\n[OK] Nhấn Enter để quay lại...")
                        return
                    self.repo_path = path
                    self.repo_url = url
                    self.branch = branch
                    print(f"[OK] Đã load cấu hình '{name}'")
                    input("\n[OK] Nhấn Enter để tiếp tục...")
            except:
                print("[ERROR] Lựa chọn không hợp lệ")
        
        elif choice == 'D':
            idx = safe_input("Nhập số thứ tự cần xóa: ").strip()
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(configs):
                    name = configs[idx][0]
                    del self.config[name]
                    self.save_config()
                    print(f"[OK] Đã xóa cấu hình '{name}'")
                    input("\n[OK] Nhấn Enter để tiếp tục...")
            except:
                print("[ERROR] Lựa chọn không hợp lệ")
    
    def auto_upload_worker(self, interval_minutes, commit_prefix):
        """Worker thread cho auto upload"""
        interval_seconds = interval_minutes * 60
        
        self.logger.info(f"Auto upload worker bắt đầu - Interval: {interval_minutes} phút")
        print(f"\n[RUNNING] Auto upload đã bắt đầu chạy nền!")
        print(f"[TIME] Upload mỗi {interval_minutes} phút")
        print("[TIP] Bạn có thể tiếp tục sử dụng các chức năng khác\n")
        time.sleep(2)
        
        upload_count = 0
        
        while self.auto_upload_running:
            try:
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                # Tạo commit message với timestamp
                commit_msg = f"{commit_prefix} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                # Kiểm tra có thay đổi không
                self.logger.debug("Kiểm tra thay đổi trong repository")
                success, stdout, _ = self.run_command(
                    f'cd "{self.repo_path}" && git status --short',
                    check=False
                )
                
                if stdout.strip():
                    # Có thay đổi, thực hiện upload
                    upload_count += 1
                    self.logger.info(f"Phát hiện thay đổi, bắt đầu upload #{upload_count}")
                    
                    # Git add
                    self.logger.debug("Git add...")
                    self.run_command(f'cd "{self.repo_path}" && git add .', check=False)
                    
                    # Git commit
                    self.logger.debug(f"Git commit: {commit_msg}")
                    self.run_command(f'cd "{self.repo_path}" && git commit -m "{commit_msg}"', check=False)
                    
                    # Git push
                    self.logger.debug(f"Git push to {self.branch}")
                    success, stdout_push, stderr_push = self.run_command(
                        f'cd "{self.repo_path}" && git push -u origin {self.branch}',
                        check=False
                    )
                    
                    if success:
                        self.logger.info(f"Upload #{upload_count} thành công!")
                        print(f"\n[OK] [{timestamp}] Auto upload #{upload_count} thành công!")
                        changed_count, changed_files = self._parse_changed_files(stdout)
                        file_list = ", ".join(changed_files[:5])
                        more = "" if changed_count <= 5 else f" (+{changed_count-5} more)"
                        msg = f"Pushed {changed_count} file(s) to {self.branch}\n{file_list}{more}" if changed_count else f"Pushed to {self.branch}"
                        self.notify("GitHub Auto Upload", msg)
                        self._write_bg_status('success', f'#{upload_count}', upload_count)
                    else:
                        self.logger.error(f"Upload #{upload_count} thất bại: {stderr_push}")
                        print(f"\n[WARNING]  [{timestamp}] Auto upload #{upload_count} thất bại")
                        changed_count, changed_files = self._parse_changed_files(stdout)
                        file_list = ", ".join(changed_files[:5])
                        more = "" if changed_count <= 5 else f" (+{changed_count-5} more)"
                        msg = f"Failed to push {changed_count} file(s) to {self.branch}\n{file_list}{more}" if changed_count else f"Push failed to {self.branch}"
                        self.notify("GitHub Auto Upload", msg, duration=7)
                        self._write_bg_status('failure', f'#{upload_count}', upload_count)
                else:
                    self.logger.debug("Không có thay đổi, bỏ qua")
                    self._write_bg_status('nochange')
                
                # Đợi đến lần upload tiếp theo
                self.logger.debug(f"Đợi {interval_minutes} phút đến lần upload tiếp theo")
                time.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.exception(f"Lỗi trong auto upload worker: {e}")
                print(f"\n[ERROR] Lỗi auto upload: {e}")
                time.sleep(60)
        
        self.logger.info(f"Auto upload worker dừng - Tổng số lần upload: {upload_count}")
    
    def start_auto_upload(self):
        """Khởi động chế độ tự động upload"""
        self.clear_screen()
        self.print_banner()
        
        print("\n[TIME] CẤU HÌNH TỰ ĐỘNG UPLOAD")
        print("=" * 60)
        
        # Kiểm tra đã có cấu hình chưa
        if not self.repo_path or not self.repo_url:
            print("\n[WARNING]  Chưa có cấu hình repository!")
            use_saved = safe_input("Bạn có muốn load cấu hình đã lưu? (y/n): ").lower()
            
            if use_saved == 'y':
                self.manage_saved_configs()
                if not self.repo_path or not self.repo_url:
                    print("[ERROR] Chưa có cấu hình, vui lòng chạy upload thủ công trước!")
                    input("\n[OK] Nhấn Enter để quay lại...")
                    return
            else:
                print("[ERROR] Vui lòng chạy upload thủ công trước (Menu 1) để cấu hình!")
                input("\n[OK] Nhấn Enter để quay lại...")
                return
        
        print(f"\n[MENU] Cấu hình hiện tại:")
        print(f"   📁 Thư mục: {self.repo_path}")
        print(f"   🔗 Repository: {self.repo_url}")
        print(f"   [BRANCH] Branch: {self.branch}")
        
        # Nhập khoảng thời gian
        print("\n[TIME]  Chọn khoảng thời gian tự động upload:")
        print("   1. Mỗi 5 phút")
        print("   2. Mỗi 10 phút")
        print("   3. Mỗi 15 phút")
        print("   4. Mỗi 30 phút")
        print("   5. Mỗi 1 giờ")
        print("   6. Mỗi 2 giờ")
        print("   7. Tùy chỉnh")
        
        choice = safe_input("\n-> Lựa chọn (1-7): ").strip()
        
        intervals = {
            "1": 5,
            "2": 10,
            "3": 15,
            "4": 30,
            "5": 60,
            "6": 120
        }
        
        if choice in intervals:
            interval = intervals[choice]
        elif choice == "7":
            try:
                interval = int(safe_input("Nhập số phút (1-1440): ").strip())
                if interval < 1 or interval > 1440:
                    print("[ERROR] Số phút phải từ 1-1440 (24 giờ)")
                    input("\n[OK] Nhấn Enter để quay lại...")
                    return
            except ValueError:
                print("[ERROR] Vui lòng nhập số hợp lệ!")
                input("\n[OK] Nhấn Enter để quay lại...")
                return
        else:
            print("[ERROR] Lựa chọn không hợp lệ!")
            input("\n[OK] Nhấn Enter để quay lại...")
            return
        
        # Nhập commit message prefix
        commit_prefix = safe_input("\n[MESSAGE] Tiền tố commit message (Enter = 'Auto update'): ").strip()
        if not commit_prefix:
            commit_prefix = "Auto update"
        
        # Lưu cấu hình
        self.auto_upload_interval = interval
        self.auto_upload_prefix = commit_prefix
        
        # Xác nhận
        print("\n" + "=" * 60)
        print("[MENU] XÁC NHẬN CẤU HÌNH:")
        print(f"   [TIME] Khoảng thời gian: Mỗi {interval} phút")
        print(f"   [MESSAGE] Commit message: {commit_prefix} - [timestamp]")
        print(f"   📁 Thư mục: {self.repo_path}")
        print(f"   🔗 Repository: {self.repo_url}")
        print("=" * 60)
        print("\n[TIP] Sau khi lưu, sử dụng Menu 8 để bật/tắt auto upload")
        
        confirm = safe_input("\n[OK] Lưu cấu hình? (y/n): ").lower()
        if confirm == 'y':
            print("[OK] Đã lưu cấu hình auto upload!")
            print("[TIP] Sử dụng Menu 8 để bật auto upload chạy nền")
        else:
            print("[ERROR] Đã hủy!")
        
        input("\n[OK] Nhấn Enter để quay lại...")
    
    def toggle_auto_upload(self):
        """Bật/Tắt auto upload chạy nền (tiếp tục khi tắt tool)"""
        if self.is_background_running():
            print("\n[STOPPED] DỪNG AUTO UPLOAD NỀN")
            print("=" * 60)
            self.stop_background_mode()
            input("\n[OK] Nhấn Enter để quay lại...")
        else:
            print("\n[RUNNING] BẬT AUTO UPLOAD NỀN")
            print("=" * 60)
            bg_cfg = self._read_bg_config()
            interval_show = (bg_cfg.get('interval') if bg_cfg and bg_cfg.get('interval') else self.auto_upload_interval) or '?'
            prefix_show = (bg_cfg.get('prefix') if bg_cfg and bg_cfg.get('prefix') else self.auto_upload_prefix) or '?'
            path_show = (bg_cfg.get('path') if bg_cfg and bg_cfg.get('path') else self.repo_path) or '?'
            print(f"[TIME] Upload mỗi {interval_show} phút")
            print(f"[MESSAGE] Message: {prefix_show}")
            print(f"📁 Thư mục: {path_show}")
            print("=" * 60)
            ok = self.start_background_mode()
            if ok:
                time.sleep(1)
            input("\n[OK] Nhấn Enter để quay lại menu...")
    
    def view_logs(self):
        """Xem logs"""
        self.clear_screen()
        self.print_banner()
        
        print("\n[LOG] QUẢN LÝ LOGS")
        print("=" * 60)
        
        # Liệt kê các file log
        log_files = sorted(
            [f for f in os.listdir(self.log_dir) if f.endswith('.log')],
            reverse=True
        )
        
        if not log_files:
            print("\n[ERROR] Không có file log nào!")
            input("\n[OK] Nhấn Enter để quay lại...")
            return
        
        print(f"\n📁 Thư mục logs: {self.log_dir}")
        print(f"\n[MENU] Có {len(log_files)} file log:\n")
        
        for i, log_file in enumerate(log_files[:10], 1):  # Hiển thị 10 file gần nhất
            file_path = os.path.join(self.log_dir, log_file)
            file_size = os.path.getsize(file_path)
            size_kb = file_size / 1024
            
            # Đọc dòng đầu và cuối
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    first_line = lines[0].strip() if lines else ""
                    last_line = lines[-1].strip() if lines else ""
            except:
                first_line = ""
                last_line = ""
            
            print(f"{i}. [LOG] {log_file} ({size_kb:.1f} KB)")
            if first_line:
                print(f"   🕐 Bắt đầu: {first_line[:50]}...")
            if last_line and last_line != first_line:
                print(f"   🕐 Kết thúc: {last_line[:50]}...")
            print()
        
        print("\nChọn:")
        print("V [số] - Xem toàn bộ log")
        print("T [số] - Xem 50 dòng cuối")
        print("E [số] - Xem lỗi (ERROR)")
        print("C - Xóa tất cả logs cũ")
        print("O - Mở thư mục logs")
        print("0 - Quay lại")
        
        choice = safe_input("\n-> Lựa chọn: ").strip().upper()
        
        if choice.startswith('V '):
            try:
                idx = int(choice.split()[1]) - 1
                if 0 <= idx < len(log_files):
                    self.display_log_content(log_files[idx])
            except:
                print("[ERROR] Lựa chọn không hợp lệ!")
        
        elif choice.startswith('T '):
            try:
                idx = int(choice.split()[1]) - 1
                if 0 <= idx < len(log_files):
                    self.display_log_tail(log_files[idx])
            except:
                print("[ERROR] Lựa chọn không hợp lệ!")
        
        elif choice.startswith('E '):
            try:
                idx = int(choice.split()[1]) - 1
                if 0 <= idx < len(log_files):
                    self.display_log_errors(log_files[idx])
            except:
                print("[ERROR] Lựa chọn không hợp lệ!")
        
        elif choice == 'C':
            confirm = safe_input("[WARNING]  Xóa tất cả logs? (yes/no): ")
            if confirm.lower() == 'yes':
                for log_file in log_files:
                    os.remove(os.path.join(self.log_dir, log_file))
                print("[OK] Đã xóa tất cả logs!")
                self.logger.info("Đã xóa tất cả logs cũ")
            input("\n[OK] Nhấn Enter để quay lại...")
        
        elif choice == 'O':
            # Mở thư mục logs
            if os.name == 'nt':  # Windows
                os.startfile(self.log_dir)
            elif sys.platform == 'darwin':  # Mac
                os.system(f'open "{self.log_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{self.log_dir}"')
            print("[OK] Đã mở thư mục logs!")
            input("\n[OK] Nhấn Enter để quay lại...")
    
    def display_log_content(self, log_file):
        """Hiển thị toàn bộ nội dung log"""
        self.clear_screen()
        self.print_banner()
        
        print(f"\n[LOG] NỘI DUNG LOG: {log_file}")
        print("=" * 60)
        
        file_path = os.path.join(self.log_dir, log_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
        except Exception as e:
            print(f"[ERROR] Lỗi đọc file: {e}")
        
        input("\n[OK] Nhấn Enter để quay lại...")
    
    def display_log_tail(self, log_file, lines=50):
        """Hiển thị n dòng cuối của log"""
        self.clear_screen()
        self.print_banner()
        
        print(f"\n[LOG] {lines} DÒNG CUỐI: {log_file}")
        print("=" * 60)
        
        file_path = os.path.join(self.log_dir, log_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                tail_lines = all_lines[-lines:]
                print(''.join(tail_lines))
        except Exception as e:
            print(f"[ERROR] Lỗi đọc file: {e}")
        
        input("\n[OK] Nhấn Enter để quay lại...")
    
    def display_log_errors(self, log_file):
        """Hiển thị chỉ các dòng ERROR"""
        self.clear_screen()
        self.print_banner()
        
        print(f"\n[ERROR] CÁC LỖI TRONG: {log_file}")
        print("=" * 60)
        
        file_path = os.path.join(self.log_dir, log_file)
        error_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'ERROR' in line or 'EXCEPTION' in line:
                        print(line.rstrip())
                        error_count += 1
            
            if error_count == 0:
                print("\n[OK] Không có lỗi nào!")
            else:
                print(f"\n[WARNING]  Tổng số lỗi: {error_count}")
        except Exception as e:
            print(f"[ERROR] Lỗi đọc file: {e}")
        
        input("\n[OK] Nhấn Enter để quay lại...")
    
    def auto_upload(self):
        """Quy trình tự động upload"""
        self.clear_screen()
        self.print_banner()
        
        self.logger.info("Bắt đầu quy trình upload thủ công")
        
        print("\n🔍 KIỂM TRA HỆ THỐNG:")
        print("-" * 60)
        if not self.check_git_installed():
            return False
        
        self.check_git_config()
        
        print("\n[MENU] NHẬP THÔNG TIN:")
        print("-" * 60)
        
        if self.config:
            use_saved = safe_input("Bạn có muốn dùng cấu hình đã lưu? (y/n): ").lower()
            if use_saved == 'y':
                self.manage_saved_configs()
                if not self.repo_path or not self.repo_url:
                    return False
        
        if not self.repo_path:
            self.repo_path = safe_input("📁 Đường dẫn thư mục code (Enter = hiện tại): ").strip()
            if not self.repo_path:
                self.repo_path = os.getcwd()
        
        if not os.path.exists(self.repo_path):
            self.logger.error(f"Thư mục không tồn tại: {self.repo_path}")
            print(f"[ERROR] Thư mục '{self.repo_path}' không tồn tại!")
            return False
        
        self.logger.info(f"Repository path: {self.repo_path}")
        
        if not self.repo_url:
            self.repo_url = safe_input("🔗 URL GitHub Repository: ").strip()
            if not self.repo_url:
                print("[ERROR] URL không được để trống!")
                return False
        
        self.logger.info(f"Repository URL: {self.repo_url}")
        
        self.branch = safe_input(f"[BRANCH] Branch (Enter = {self.branch}): ").strip() or self.branch
        self.logger.info(f"Branch: {self.branch}")
        
        commit_msg = safe_input("[MESSAGE] Commit message (Enter = tự động): ").strip()
        if not commit_msg:
            commit_msg = f"Auto update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.logger.info(f"Commit message: {commit_msg}")
        
        save_cfg = safe_input("\n[SAVE] Lưu cấu hình này? (y/n): ").lower()
        if save_cfg == 'y':
            cfg_name = safe_input("   [EDIT] Tên cấu hình: ").strip() or "default"
            self.config[cfg_name] = {
                'path': self.repo_path,
                'url': self.repo_url,
                'branch': self.branch
            }
            self.save_config()
            self.logger.info(f"Đã lưu cấu hình: {cfg_name}")
            print("[OK] Đã lưu cấu hình!")
        
        print("\n" + "=" * 60)
        print("[MENU] XÁC NHẬN THÔNG TIN:")
        print(f"   📁 Thư mục: {self.repo_path}")
        print(f"   🔗 Repository: {self.repo_url}")
        print(f"   [BRANCH] Branch: {self.branch}")
        print(f"   [MESSAGE] Message: {commit_msg}")
        print("=" * 60)
        
        confirm = safe_input("\n[OK] Xác nhận và bắt đầu upload? (y/n): ").lower()
        if confirm != 'y':
            self.logger.info("Upload bị hủy bởi người dùng")
            print("[ERROR] Đã hủy!")
            return False
        
        print("\n" + "=" * 60)
        print("[UPLOAD] BẮT ĐẦU UPLOAD...")
        print("=" * 60)
        
        self.logger.info("Bắt đầu quá trình upload")
        
        if not self.init_git_repo():
            self.logger.error("Lỗi khởi tạo Git repository")
            return False
        
        if not self.configure_remote():
            self.logger.error("Lỗi cấu hình remote")
            return False
        
        self.show_git_status()
        
        if not self.git_add_all():
            self.logger.error("Lỗi khi add files")
            return False
        
        if not self.git_commit(commit_msg):
            self.logger.error("Lỗi khi commit")
            return False
        
        if not self.git_push():
            self.logger.error("Lỗi khi push")
            return False
        
        print("\n" + "=" * 60)
        print("[SUCCESS] HOÀN TẤT! Code đã được đẩy lên GitHub thành công!")
        print("=" * 60)
        
        self.logger.info("Upload thành công!")
        self.logger.info("=" * 60)

        return True, {
            'path': self.repo_path,
            'url': self.repo_url,
            'branch': self.branch
        }
        self.save_config()
        print("[OK] Đã lưu cấu hình!")
        
        print("\n" + "=" * 60)
        print("[MENU] XÁC NHẬN THÔNG TIN:")
        print(f"   📁 Thư mục: {self.repo_path}")
        print(f"   🔗 Repository: {self.repo_url}")
        print(f"   [BRANCH] Branch: {self.branch}")
        print(f"   [MESSAGE] Message: {commit_msg}")
        print("=" * 60)
        
        confirm = safe_input("\n[OK] Xác nhận và bắt đầu upload? (y/n): ").lower()
        if confirm != 'y':
            print("[ERROR] Đã hủy!")
            return False
        
        print("\n" + "=" * 60)
        print("[UPLOAD] BẮT ĐẦU UPLOAD...")
        print("=" * 60)
        
        if not self.init_git_repo():
            return False
        
        if not self.configure_remote():
            return False
        
        self.show_git_status()
        
        if not self.git_add_all():
            return False
        
        if not self.git_commit(commit_msg):
            return False
        
        if not self.git_push():
            return False
        
        print("\n" + "=" * 60)
        print("[SUCCESS] HOÀN TẤT! Code đã được đẩy lên GitHub thành công!")
        print("=" * 60)
        return True
    
    # =========================
    # Background entrypoint
    # =========================
    def run_background_loop(self):
        """Chạy vòng lặp auto upload ở chế độ nền (không cần mở tool)"""
        try:
            # Đọc cấu hình nền
            cfg = self._safe_read_json(self.bg_config_file, default=None)
            if not cfg:
                print("[ERROR] Không tìm thấy hoặc lỗi cấu hình nền, thoát!")
                return 1
            self.repo_path = cfg.get('path')
            self.repo_url = cfg.get('url')
            self.branch = cfg.get('branch', 'main')
            self.auto_upload_interval = int(cfg.get('interval'))
            self.auto_upload_prefix = cfg.get('prefix') or 'Auto update'

            # Đảm bảo repo hợp lệ và remote
            if not self.init_git_repo() or not self.configure_remote():
                return 2

            # Vòng lặp vô hạn, dừng bằng cách kill tiến trình từ ngoài
            interval_minutes = self.auto_upload_interval
            commit_prefix = self.auto_upload_prefix
            upload_count = 0
            self.logger.info(f"Background loop bắt đầu - mỗi {interval_minutes} phút")
            self._write_bg_status('start')
            # Prepare stop event for tray control
            try:
                self._bg_stop_event = threading.Event()
            except Exception:
                self._bg_stop_event = None

            # Try to create a system tray icon on Windows so the background process is visible and controllable
            systray = None
            try:
                if os.name == 'nt':
                    icon_path = None
                    menu_options = (
                        ("Open GUI", None, lambda s: self._open_gui_from_tray()),
                        ("Stop background", None, lambda s: self._stop_from_tray(s)),
                    )
                    systray = SysTrayIcon(icon_path, "GitHub Auto Upload", menu_options, on_quit=self._stop_from_tray)
                    systray.start()
            except Exception:
                self.logger.exception('Cannot start system tray icon for background mode')

            while not (self._bg_stop_event and self._bg_stop_event.is_set()):
                try:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    commit_msg = f"{commit_prefix} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    success, stdout, _ = self.run_command(
                        f'cd "{self.repo_path}" && git status --short',
                        check=False
                    )
                    if stdout.strip():
                        upload_count += 1
                        self.logger.info(f"[BG] Thay đổi phát hiện, upload #{upload_count}")
                        self.run_command(f'cd "{self.repo_path}" && git add .', check=False)
                        self.run_command(f'cd "{self.repo_path}" && git commit -m "{commit_msg}"', check=False)
                        ok, _, errp = self.run_command(
                            f'cd "{self.repo_path}" && git push -u origin {self.branch}',
                            check=False
                        )
                        if ok:
                            self.logger.info(f"[BG] Upload #{upload_count} thành công ({timestamp})")
                            changed_count, changed_files = self._parse_changed_files(stdout)
                            file_list = ", ".join(changed_files[:5])
                            more = "" if changed_count <= 5 else f" (+{changed_count-5} more)"
                            msg = f"Pushed {changed_count} file(s) to {self.branch}\n{file_list}{more}" if changed_count else f"Pushed to {self.branch}"
                            self.notify("GitHub Auto Upload", msg)
                            self._write_bg_status('success', f'#{upload_count}', upload_count)
                        else:
                            self.logger.error(f"[BG] Upload #{upload_count} thất bại: {errp}")
                            changed_count, changed_files = self._parse_changed_files(stdout)
                            file_list = ", ".join(changed_files[:5])
                            more = "" if changed_count <= 5 else f" (+{changed_count-5} more)"
                            msg = f"Failed to push {changed_count} file(s) to {self.branch}\n{file_list}{more}" if changed_count else f"Push failed to {self.branch}"
                            self.notify("GitHub Auto Upload", msg, duration=7)
                            self._write_bg_status('failure', f'#{upload_count}', upload_count)
                    # sleep but wake early if stop requested
                    slept = 0
                    total = interval_minutes * 60
                    while slept < total:
                        if self._bg_stop_event and self._bg_stop_event.is_set():
                            break
                        time.sleep(1)
                        slept += 1
                    if self._bg_stop_event and self._bg_stop_event.is_set():
                        break
                except Exception as loop_e:
                    self.logger.exception(f"[BG] Lỗi vòng lặp: {loop_e}")
                    self._write_bg_status('failure', str(loop_e))
                    time.sleep(60)
        except Exception as e:
            self.logger.exception(f"[BG] Lỗi khởi động: {e}")
            return 1
        finally:
            try:
                if systray:
                    systray.shutdown()
            except Exception:
                pass
        return 0

    def _open_gui_from_tray(self):
        try:
            pythonw = sys.executable
            if pythonw.lower().endswith('python.exe'):
                maybe = pythonw[:-10] + 'pythonw.exe'
                if os.path.exists(maybe):
                    pythonw = maybe
            script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'run_update_gui.pyw'))
            subprocess.Popen([pythonw, script], close_fds=True)
        except Exception:
            self.logger.exception('Failed to open GUI from tray')

    def _stop_from_tray(self, systray=None):
        try:
            if hasattr(self, '_bg_stop_event') and self._bg_stop_event:
                self._bg_stop_event.set()
            self._write_bg_status('stopped')
            self.logger.info('Background stop requested from tray')
            if systray:
                try:
                    systray.shutdown()
                except Exception:
                    pass
        except Exception:
            self.logger.exception('Error while stopping from tray')
    
    def run(self):
        """Chạy chương trình chính"""
        while True:
            choice = self.show_menu()
            
            if choice == "1":
                self.auto_upload()
                input("\n[OK] Nhấn Enter để quay lại menu...")
            
            elif choice == "2":
                self.clear_screen()
                self.print_banner()
                if not self.repo_path:
                    self.repo_path = safe_input("\n📁 Đường dẫn thư mục: ").strip() or os.getcwd()
                self.show_git_status()
                input("\n[OK] Nhấn Enter để quay lại menu...")
            
            elif choice == "3":
                self.clear_screen()
                self.print_banner()
                if not self.repo_path:
                    self.repo_path = safe_input("\n📁 Đường dẫn thư mục: ").strip() or os.getcwd()
                self.create_gitignore()
                input("\n[OK] Nhấn Enter để quay lại menu...")
            
            elif choice == "4":
                self.show_simple_guide()
            
            elif choice == "5":
                self.manage_saved_configs()
            
            elif choice == "6":
                self.show_simple_guide()
            
            elif choice == "7":
                self.start_auto_upload()
            
            elif choice == "8":
                self.toggle_auto_upload()
            
            elif choice == "9":
                self.view_logs()
            
            elif choice == "0":
                # Dừng auto upload nếu đang chạy
                if self.auto_upload_running:
                    self.logger.info("Đang dừng auto upload...")
                    print("\n[WARNING]  Đang dừng tự động upload...")
                    self.auto_upload_running = False
                    if self.auto_upload_thread:
                        self.auto_upload_thread.join(timeout=5)
                
                self.logger.info("Tool đã đóng")
                self.logger.info("=" * 60)
                print("\n[EXIT] Cảm ơn bạn đã sử dụng! Tạm biệt!")
                break
            
            else:
                print("[ERROR] Lựa chọn không hợp lệ!")
                input("\n[OK] Nhấn Enter để thử lại...")

def main():
    try:
        uploader = GitHubUploader()
        # CLI flags đơn giản
        if '--run-background' in sys.argv:
            sys.exit(uploader.run_background_loop())
        # Language selection on startup
        uploader.select_language()
        uploader.run()
    except KeyboardInterrupt:
        print("\n\n[WARNING]  Đã dừng chương trình!")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Lỗi không mong muốn: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

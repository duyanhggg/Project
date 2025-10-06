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
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self):
        """Lưu cấu hình"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Không thể lưu cấu hình: {e}")
    
    def clear_screen(self):
        """Xóa màn hình console"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        """In banner chào mừng"""
        print("=" * 60)
        print("       🚀 GITHUB AUTO UPLOAD TOOL PRO 🚀")
        print("    Tự động đẩy code lên GitHub với nhiều tính năng")
        print("=" * 60)
    
    def run_command(self, command, check=True):
        """Chạy lệnh shell và trả về kết quả"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=check,
                capture_output=True,
                text=True,
                encoding='utf-8'
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
            print("❌ Git chưa được cài đặt!")
            print("\n📥 HƯỚNG DẪN CÀI ĐẶT GIT:")
            print("   🪟 Windows: https://git-scm.com/download/win")
            print("   🍎 Mac: brew install git")
            print("   🐧 Linux: sudo apt install git")
            return False
        self.logger.info(f"Git đã cài đặt: {stdout.strip()}")
        print(f"✅ {stdout.strip()}")
        return True
    
    def check_git_config(self):
        """Kiểm tra cấu hình Git"""
        success, name, _ = self.run_command("git config --global user.name", check=False)
        success2, email, _ = self.run_command("git config --global user.email", check=False)
        
        if not success or not success2 or not name.strip() or not email.strip():
            print("\n⚠️  Git chưa được cấu hình!")
            print("\n📝 Vui lòng cấu hình Git:")
            
            if not name.strip():
                user_name = input("   👤 Nhập tên của bạn: ").strip()
                if user_name:
                    self.run_command(f'git config --global user.name "{user_name}"')
            
            if not email.strip():
                user_email = input("   📧 Nhập email của bạn: ").strip()
                if user_email:
                    self.run_command(f'git config --global user.email "{user_email}"')
            
            print("✅ Đã cấu hình Git!")
        else:
            print(f"✅ Git User: {name.strip()} <{email.strip()}>")
    
    def create_gitignore(self):
        """Tạo file .gitignore"""
        gitignore_path = os.path.join(self.repo_path, ".gitignore")
        
        if os.path.exists(gitignore_path):
            print("ℹ️  File .gitignore đã tồn tại")
            return
        
        print("\n📝 Tạo file .gitignore")
        print("Chọn template:")
        print("1. 🐍 Python")
        print("2. 📦 Node.js")
        print("3. ☕ Java")
        print("4. 🔧 C/C++")
        print("0. ❌ Bỏ qua")
        
        choice = input("\nLựa chọn (0-4): ").strip()
        
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
                print("✅ Đã tạo .gitignore")
            except Exception as e:
                print(f"❌ Lỗi tạo .gitignore: {e}")
    
    def show_git_status(self):
        """Hiển thị trạng thái Git"""
        print("\n📊 TRẠNG THÁI GIT:")
        success, stdout, _ = self.run_command(f'cd "{self.repo_path}" && git status --short')
        if success and stdout.strip():
            print(stdout)
        else:
            print("   ℹ️  Không có thay đổi nào")
    
    def init_git_repo(self):
        """Khởi tạo Git repository nếu chưa có"""
        # Fix lỗi dubious ownership
        safe_dir_cmd = f'git config --global --add safe.directory "{self.repo_path}"'
        self.run_command(safe_dir_cmd, check=False)
        
        if not os.path.exists(os.path.join(self.repo_path, ".git")):
            print("📦 Đang khởi tạo Git repository...")
            success, _, error = self.run_command(f'cd "{self.repo_path}" && git init')
            if success:
                print("✅ Đã khởi tạo Git repository")
                
                create = input("Bạn có muốn tạo file .gitignore? (y/n): ").lower()
                if create == 'y':
                    self.create_gitignore()
            else:
                print(f"❌ Lỗi khởi tạo: {error}")
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
            print(f"📡 Remote hiện tại: {current_url}")
            
            if current_url != self.repo_url:
                change = input("URL khác. Cập nhật? (y/n): ").lower()
                if change == 'y':
                    self.run_command(f'cd "{self.repo_path}" && git remote set-url origin {self.repo_url}')
                    print("✅ Đã cập nhật remote URL")
        else:
            print("📡 Đang thêm remote repository...")
            success, _, error = self.run_command(
                f'cd "{self.repo_path}" && git remote add origin {self.repo_url}'
            )
            if success:
                print("✅ Đã thêm remote repository")
            else:
                print(f"❌ Lỗi thêm remote: {error}")
                return False
        return True
    
    def git_add_all(self):
        """Git add tất cả file"""
        print("\n📝 Đang thêm files vào staging...")
        
        success, stdout, _ = self.run_command(
            f'cd "{self.repo_path}" && git status --short',
            check=False
        )
        if stdout.strip():
            print("Files sẽ được thêm:")
            print(stdout)
        
        success, _, error = self.run_command(f'cd "{self.repo_path}" && git add .')
        if success:
            print("✅ Đã thêm tất cả files")
            return True
        else:
            print(f"❌ Lỗi khi thêm files: {error}")
            return False
    
    def git_commit(self, message):
        """Git commit với message"""
        print(f"\n💬 Đang commit với message: '{message}'")
        success, stdout, error = self.run_command(
            f'cd "{self.repo_path}" && git commit -m "{message}"',
            check=False
        )
        if success:
            print("✅ Đã commit thành công")
            print(stdout)
            return True
        else:
            if "nothing to commit" in error:
                print("ℹ️  Không có thay đổi nào để commit")
                return True
            print(f"❌ Lỗi khi commit: {error}")
            return False
    
    def git_push(self, force=False):
        """Git push lên remote"""
        print(f"\n🚀 Đang đẩy code lên branch '{self.branch}'...")
        
        success, _, _ = self.run_command(
            f'cd "{self.repo_path}" && git rev-parse --verify {self.branch}',
            check=False
        )
        
        if not success:
            print(f"🌿 Branch '{self.branch}' chưa tồn tại, đang tạo mới...")
            self.run_command(f'cd "{self.repo_path}" && git checkout -b {self.branch}')
        
        force_flag = " --force" if force else ""
        success, stdout, error = self.run_command(
            f'cd "{self.repo_path}" && git push -u origin {self.branch}{force_flag}',
            check=False
        )
        
        if success:
            print("✅ Đã đẩy code lên GitHub thành công! 🎉")
            print(stdout)
            return True
        else:
            print(f"❌ Lỗi khi push: {error}")
            
            if "rejected" in error or "non-fast-forward" in error:
                print("\n💡 Remote có commits mới hơn!")
                print("Lựa chọn:")
                print("1. Pull và merge (khuyên dùng)")
                print("2. Force push (nguy hiểm)")
                print("0. Hủy")
                
                choice = input("\nLựa chọn (0-2): ").strip()
                
                if choice == "1":
                    print("🔄 Đang pull code...")
                    self.run_command(f'cd "{self.repo_path}" && git pull origin {self.branch}')
                    return self.git_push()
                elif choice == "2":
                    confirm = input("⚠️  Bạn chắc chắn muốn force push? (yes/no): ")
                    if confirm.lower() == "yes":
                        return self.git_push(force=True)
            
            elif "Authentication" in error or "denied" in error:
                print("\n❌ LỖI XÁC THỰC!")
                print("Vui lòng kiểm tra:")
                print("1. Token/Password đã đúng chưa?")
                print("2. SSH key đã được thêm vào GitHub chưa?")
            
            return False
    
    def show_menu(self):
        """Hiển thị menu chính"""
        self.clear_screen()
        self.print_banner()
        
        # Hiển thị trạng thái auto upload
        if self.auto_upload_running:
            print("\n🟢 TỰ ĐỘNG UPLOAD: ĐANG CHẠY NỀN")
        else:
            print("\n⚪ TỰ ĐỘNG UPLOAD: TẮT")
        
        print("\n📋 MENU CHÍNH:")
        print("1. 🚀 Upload code lên GitHub")
        print("2. 📊 Xem trạng thái Git")
        print("3. 📝 Tạo/Sửa .gitignore")
        print("4. 🔐 Hướng dẫn xác thực GitHub")
        print("5. 💾 Quản lý cấu hình đã lưu")
        print("6. 📚 Hướng dẫn cài đặt & sử dụng")
        print("7. ⏰ Cấu hình tự động upload")
        
        if self.auto_upload_running:
            print("8. 🔴 Dừng auto upload đang chạy")
        else:
            print("8. 🟢 Bật auto upload (chạy nền)")
        
        print("9. 📄 Xem logs")
        print("0. 👋 Thoát")
        
        return input("\n➤ Chọn chức năng (0-9): ").strip()
    
    def show_simple_guide(self):
        """Hiển thị hướng dẫn đơn giản"""
        self.clear_screen()
        self.print_banner()
        
        print("\n📚 HƯỚNG DẪN SỬ DỤNG\n")
        print("=" * 60)
        
        print("\n🔧 1. CÀI ĐẶT GIT:")
        print("   🪟 Windows: https://git-scm.com/download/win")
        print("   🍎 Mac: brew install git")
        print("   🐧 Linux: sudo apt install git")
        
        print("\n⚙️  2. CẤU HÌNH GIT:")
        print('   git config --global user.name "Tên"')
        print('   git config --global user.email "email@example.com"')
        
        print("\n🔑 3. TẠO TOKEN GITHUB:")
        print("   📍 Bước 1: Vào https://github.com/settings/tokens")
        print("   📍 Bước 2: Generate new token -> Tokens (classic)")
        print("   📍 Bước 3: Chọn quyền: repo, workflow")
        print("   📍 Bước 4: Copy token (chỉ hiện 1 lần!)")
        
        print("\n🔐 4. SỬ DỤNG TOKEN:")
        print("   • Khi push lần đầu, Git hỏi username & password")
        print("   • Username: tên GitHub của bạn")
        print("   • Password: DÁN TOKEN vào (KHÔNG phải password GitHub)")
        print("   • Token sẽ được lưu tự động")
        
        print("\n🚀 5. UPLOAD CODE:")
        print("   • Chọn menu 1")
        print("   • Nhập đường dẫn thư mục code")
        print("   • Nhập URL repository")
        print("   • Nhập branch (Enter = main)")
        print("   • Nhập commit message")
        print("   • Xác nhận và đợi!")
        
        print("\n⚠️  6. XỬ LÝ LỖI:")
        print("   • 'git not recognized': Khởi động lại máy")
        print("   • 'Authentication failed': Token/Password sai")
        print("   • 'rejected': Chọn Pull và merge")
        
        print("\n" + "=" * 60)
        
        input("\n✅ Nhấn Enter để quay lại menu...")
    
    def manage_saved_configs(self):
        """Quản lý các cấu hình đã lưu"""
        self.clear_screen()
        self.print_banner()
        
        if not self.config:
            print("\n📭 Chưa có cấu hình nào được lưu")
            input("\n✅ Nhấn Enter để quay lại...")
            return
        
        print("\n💾 CÁC CẤU HÌNH ĐÃ LƯU:\n")
        
        configs = list(self.config.items())
        for i, (name, cfg) in enumerate(configs, 1):
            print(f"{i}. 📦 {name}")
            print(f"   📁 Thư mục: {cfg.get('path', 'N/A')}")
            print(f"   🔗 Repository: {cfg.get('url', 'N/A')}")
            print(f"   🌿 Branch: {cfg.get('branch', 'N/A')}\n")
        
        print("Chọn:")
        print("L - 📥 Load cấu hình")
        print("D - 🗑️  Xóa cấu hình")
        print("0 - ↩️  Quay lại")
        
        choice = input("\n➤ Lựa chọn: ").strip().upper()
        
        if choice == 'L':
            idx = input("Nhập số thứ tự: ").strip()
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(configs):
                    name, cfg = configs[idx]
                    self.repo_path = cfg.get('path')
                    self.repo_url = cfg.get('url')
                    self.branch = cfg.get('branch', 'main')
                    print(f"✅ Đã load cấu hình '{name}'")
                    input("\n✅ Nhấn Enter để tiếp tục...")
            except:
                print("❌ Lựa chọn không hợp lệ")
        
        elif choice == 'D':
            idx = input("Nhập số thứ tự cần xóa: ").strip()
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(configs):
                    name = configs[idx][0]
                    del self.config[name]
                    self.save_config()
                    print(f"✅ Đã xóa cấu hình '{name}'")
                    input("\n✅ Nhấn Enter để tiếp tục...")
            except:
                print("❌ Lựa chọn không hợp lệ")
    
    def auto_upload_worker(self, interval_minutes, commit_prefix):
        """Worker thread cho auto upload"""
        interval_seconds = interval_minutes * 60
        
        self.logger.info(f"Auto upload worker bắt đầu - Interval: {interval_minutes} phút")
        print(f"\n🟢 Auto upload đã bắt đầu chạy nền!")
        print(f"⏰ Upload mỗi {interval_minutes} phút")
        print("💡 Bạn có thể tiếp tục sử dụng các chức năng khác\n")
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
                        print(f"\n✅ [{timestamp}] Auto upload #{upload_count} thành công!")
                    else:
                        self.logger.error(f"Upload #{upload_count} thất bại: {stderr_push}")
                        print(f"\n⚠️  [{timestamp}] Auto upload #{upload_count} thất bại")
                else:
                    self.logger.debug("Không có thay đổi, bỏ qua")
                
                # Đợi đến lần upload tiếp theo
                self.logger.debug(f"Đợi {interval_minutes} phút đến lần upload tiếp theo")
                time.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.exception(f"Lỗi trong auto upload worker: {e}")
                print(f"\n❌ Lỗi auto upload: {e}")
                time.sleep(60)
        
        self.logger.info(f"Auto upload worker dừng - Tổng số lần upload: {upload_count}")
    
    def start_auto_upload(self):
        """Khởi động chế độ tự động upload"""
        self.clear_screen()
        self.print_banner()
        
        print("\n⏰ CẤU HÌNH TỰ ĐỘNG UPLOAD")
        print("=" * 60)
        
        # Kiểm tra đã có cấu hình chưa
        if not self.repo_path or not self.repo_url:
            print("\n⚠️  Chưa có cấu hình repository!")
            use_saved = input("Bạn có muốn load cấu hình đã lưu? (y/n): ").lower()
            
            if use_saved == 'y':
                self.manage_saved_configs()
                if not self.repo_path or not self.repo_url:
                    print("❌ Chưa có cấu hình, vui lòng chạy upload thủ công trước!")
                    input("\n✅ Nhấn Enter để quay lại...")
                    return
            else:
                print("❌ Vui lòng chạy upload thủ công trước (Menu 1) để cấu hình!")
                input("\n✅ Nhấn Enter để quay lại...")
                return
        
        print(f"\n📋 Cấu hình hiện tại:")
        print(f"   📁 Thư mục: {self.repo_path}")
        print(f"   🔗 Repository: {self.repo_url}")
        print(f"   🌿 Branch: {self.branch}")
        
        # Nhập khoảng thời gian
        print("\n⏱️  Chọn khoảng thời gian tự động upload:")
        print("   1. Mỗi 5 phút")
        print("   2. Mỗi 10 phút")
        print("   3. Mỗi 15 phút")
        print("   4. Mỗi 30 phút")
        print("   5. Mỗi 1 giờ")
        print("   6. Mỗi 2 giờ")
        print("   7. Tùy chỉnh")
        
        choice = input("\n➤ Lựa chọn (1-7): ").strip()
        
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
                interval = int(input("Nhập số phút (1-1440): ").strip())
                if interval < 1 or interval > 1440:
                    print("❌ Số phút phải từ 1-1440 (24 giờ)")
                    input("\n✅ Nhấn Enter để quay lại...")
                    return
            except ValueError:
                print("❌ Vui lòng nhập số hợp lệ!")
                input("\n✅ Nhấn Enter để quay lại...")
                return
        else:
            print("❌ Lựa chọn không hợp lệ!")
            input("\n✅ Nhấn Enter để quay lại...")
            return
        
        # Nhập commit message prefix
        commit_prefix = input("\n💬 Tiền tố commit message (Enter = 'Auto update'): ").strip()
        if not commit_prefix:
            commit_prefix = "Auto update"
        
        # Lưu cấu hình
        self.auto_upload_interval = interval
        self.auto_upload_prefix = commit_prefix
        
        # Xác nhận
        print("\n" + "=" * 60)
        print("📋 XÁC NHẬN CẤU HÌNH:")
        print(f"   ⏰ Khoảng thời gian: Mỗi {interval} phút")
        print(f"   💬 Commit message: {commit_prefix} - [timestamp]")
        print(f"   📁 Thư mục: {self.repo_path}")
        print(f"   🔗 Repository: {self.repo_url}")
        print("=" * 60)
        print("\n💡 Sau khi lưu, sử dụng Menu 8 để bật/tắt auto upload")
        
        confirm = input("\n✅ Lưu cấu hình? (y/n): ").lower()
        if confirm == 'y':
            print("✅ Đã lưu cấu hình auto upload!")
            print("💡 Sử dụng Menu 8 để bật auto upload chạy nền")
        else:
            print("❌ Đã hủy!")
        
        input("\n✅ Nhấn Enter để quay lại...")
    
    def toggle_auto_upload(self):
        """Bật/Tắt auto upload"""
        if self.auto_upload_running:
            # Đang chạy -> Dừng lại
            print("\n🔴 DỪNG AUTO UPLOAD")
            print("=" * 60)
            self.auto_upload_running = False
            if self.auto_upload_thread:
                print("⏳ Đang dừng thread...")
                self.auto_upload_thread.join(timeout=3)
            print("✅ Đã dừng auto upload!")
            input("\n✅ Nhấn Enter để quay lại...")
        else:
            # Chưa chạy -> Bật lên
            if not self.auto_upload_interval or not self.auto_upload_prefix:
                print("\n⚠️  Chưa có cấu hình auto upload!")
                print("💡 Vui lòng chạy Menu 7 để cấu hình trước")
                input("\n✅ Nhấn Enter để quay lại...")
                return
            
            if not self.repo_path or not self.repo_url:
                print("\n⚠️  Chưa có cấu hình repository!")
                print("💡 Vui lòng chạy Menu 1 để cấu hình trước")
                input("\n✅ Nhấn Enter để quay lại...")
                return
            
            print("\n🟢 BẬT AUTO UPLOAD")
            print("=" * 60)
            print(f"⏰ Upload mỗi {self.auto_upload_interval} phút")
            print(f"💬 Message: {self.auto_upload_prefix}")
            print(f"📁 Thư mục: {self.repo_path}")
            print("=" * 60)
            
            self.auto_upload_running = True
            self.auto_upload_thread = threading.Thread(
                target=self.auto_upload_worker,
                args=(self.auto_upload_interval, self.auto_upload_prefix),
                daemon=True
            )
            self.auto_upload_thread.start()
            
            time.sleep(2)
            input("\n✅ Nhấn Enter để quay lại menu (auto upload chạy nền)...")
    
    def view_logs(self):
        """Xem logs"""
        self.clear_screen()
        self.print_banner()
        
        print("\n📄 QUẢN LÝ LOGS")
        print("=" * 60)
        
        # Liệt kê các file log
        log_files = sorted(
            [f for f in os.listdir(self.log_dir) if f.endswith('.log')],
            reverse=True
        )
        
        if not log_files:
            print("\n❌ Không có file log nào!")
            input("\n✅ Nhấn Enter để quay lại...")
            return
        
        print(f"\n📁 Thư mục logs: {self.log_dir}")
        print(f"\n📋 Có {len(log_files)} file log:\n")
        
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
            
            print(f"{i}. 📄 {log_file} ({size_kb:.1f} KB)")
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
        
        choice = input("\n➤ Lựa chọn: ").strip().upper()
        
        if choice.startswith('V '):
            try:
                idx = int(choice.split()[1]) - 1
                if 0 <= idx < len(log_files):
                    self.display_log_content(log_files[idx])
            except:
                print("❌ Lựa chọn không hợp lệ!")
        
        elif choice.startswith('T '):
            try:
                idx = int(choice.split()[1]) - 1
                if 0 <= idx < len(log_files):
                    self.display_log_tail(log_files[idx])
            except:
                print("❌ Lựa chọn không hợp lệ!")
        
        elif choice.startswith('E '):
            try:
                idx = int(choice.split()[1]) - 1
                if 0 <= idx < len(log_files):
                    self.display_log_errors(log_files[idx])
            except:
                print("❌ Lựa chọn không hợp lệ!")
        
        elif choice == 'C':
            confirm = input("⚠️  Xóa tất cả logs? (yes/no): ")
            if confirm.lower() == 'yes':
                for log_file in log_files:
                    os.remove(os.path.join(self.log_dir, log_file))
                print("✅ Đã xóa tất cả logs!")
                self.logger.info("Đã xóa tất cả logs cũ")
            input("\n✅ Nhấn Enter để quay lại...")
        
        elif choice == 'O':
            # Mở thư mục logs
            if os.name == 'nt':  # Windows
                os.startfile(self.log_dir)
            elif sys.platform == 'darwin':  # Mac
                os.system(f'open "{self.log_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{self.log_dir}"')
            print("✅ Đã mở thư mục logs!")
            input("\n✅ Nhấn Enter để quay lại...")
    
    def display_log_content(self, log_file):
        """Hiển thị toàn bộ nội dung log"""
        self.clear_screen()
        self.print_banner()
        
        print(f"\n📄 NỘI DUNG LOG: {log_file}")
        print("=" * 60)
        
        file_path = os.path.join(self.log_dir, log_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
        except Exception as e:
            print(f"❌ Lỗi đọc file: {e}")
        
        input("\n✅ Nhấn Enter để quay lại...")
    
    def display_log_tail(self, log_file, lines=50):
        """Hiển thị n dòng cuối của log"""
        self.clear_screen()
        self.print_banner()
        
        print(f"\n📄 {lines} DÒNG CUỐI: {log_file}")
        print("=" * 60)
        
        file_path = os.path.join(self.log_dir, log_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                tail_lines = all_lines[-lines:]
                print(''.join(tail_lines))
        except Exception as e:
            print(f"❌ Lỗi đọc file: {e}")
        
        input("\n✅ Nhấn Enter để quay lại...")
    
    def display_log_errors(self, log_file):
        """Hiển thị chỉ các dòng ERROR"""
        self.clear_screen()
        self.print_banner()
        
        print(f"\n❌ CÁC LỖI TRONG: {log_file}")
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
                print("\n✅ Không có lỗi nào!")
            else:
                print(f"\n⚠️  Tổng số lỗi: {error_count}")
        except Exception as e:
            print(f"❌ Lỗi đọc file: {e}")
        
        input("\n✅ Nhấn Enter để quay lại...")
    
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
        
        print("\n📋 NHẬP THÔNG TIN:")
        print("-" * 60)
        
        if self.config:
            use_saved = input("Bạn có muốn dùng cấu hình đã lưu? (y/n): ").lower()
            if use_saved == 'y':
                self.manage_saved_configs()
                if not self.repo_path or not self.repo_url:
                    return False
        
        if not self.repo_path:
            self.repo_path = input("📁 Đường dẫn thư mục code (Enter = hiện tại): ").strip()
            if not self.repo_path:
                self.repo_path = os.getcwd()
        
        if not os.path.exists(self.repo_path):
            self.logger.error(f"Thư mục không tồn tại: {self.repo_path}")
            print(f"❌ Thư mục '{self.repo_path}' không tồn tại!")
            return False
        
        self.logger.info(f"Repository path: {self.repo_path}")
        
        if not self.repo_url:
            self.repo_url = input("🔗 URL GitHub Repository: ").strip()
            if not self.repo_url:
                print("❌ URL không được để trống!")
                return False
        
        self.logger.info(f"Repository URL: {self.repo_url}")
        
        self.branch = input(f"🌿 Branch (Enter = {self.branch}): ").strip() or self.branch
        self.logger.info(f"Branch: {self.branch}")
        
        commit_msg = input("💬 Commit message (Enter = tự động): ").strip()
        if not commit_msg:
            commit_msg = f"Auto update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.logger.info(f"Commit message: {commit_msg}")
        
        save_cfg = input("\n💾 Lưu cấu hình này? (y/n): ").lower()
        if save_cfg == 'y':
            cfg_name = input("   📝 Tên cấu hình: ").strip() or "default"
            self.config[cfg_name] = {
                'path': self.repo_path,
                'url': self.repo_url,
                'branch': self.branch
            }
            self.save_config()
            self.logger.info(f"Đã lưu cấu hình: {cfg_name}")
            print("✅ Đã lưu cấu hình!")
        
        print("\n" + "=" * 60)
        print("📋 XÁC NHẬN THÔNG TIN:")
        print(f"   📁 Thư mục: {self.repo_path}")
        print(f"   🔗 Repository: {self.repo_url}")
        print(f"   🌿 Branch: {self.branch}")
        print(f"   💬 Message: {commit_msg}")
        print("=" * 60)
        
        confirm = input("\n✅ Xác nhận và bắt đầu upload? (y/n): ").lower()
        if confirm != 'y':
            self.logger.info("Upload bị hủy bởi người dùng")
            print("❌ Đã hủy!")
            return False
        
        print("\n" + "=" * 60)
        print("🚀 BẮT ĐẦU UPLOAD...")
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
        print("🎉 HOÀN TẤT! Code đã được đẩy lên GitHub thành công!")
        print("=" * 60)
        
        self.logger.info("Upload thành công!")
        self.logger.info("=" * 60)

        return True, {
            'path': self.repo_path,
            'url': self.repo_url,
            'branch': self.branch
        }
        self.save_config()
        print("✅ Đã lưu cấu hình!")
        
        print("\n" + "=" * 60)
        print("📋 XÁC NHẬN THÔNG TIN:")
        print(f"   📁 Thư mục: {self.repo_path}")
        print(f"   🔗 Repository: {self.repo_url}")
        print(f"   🌿 Branch: {self.branch}")
        print(f"   💬 Message: {commit_msg}")
        print("=" * 60)
        
        confirm = input("\n✅ Xác nhận và bắt đầu upload? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Đã hủy!")
            return False
        
        print("\n" + "=" * 60)
        print("🚀 BẮT ĐẦU UPLOAD...")
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
        print("🎉 HOÀN TẤT! Code đã được đẩy lên GitHub thành công!")
        print("=" * 60)
        return True
    
    def run(self):
        """Chạy chương trình chính"""
        while True:
            choice = self.show_menu()
            
            if choice == "1":
                self.auto_upload()
                input("\n✅ Nhấn Enter để quay lại menu...")
            
            elif choice == "2":
                self.clear_screen()
                self.print_banner()
                if not self.repo_path:
                    self.repo_path = input("\n📁 Đường dẫn thư mục: ").strip() or os.getcwd()
                self.show_git_status()
                input("\n✅ Nhấn Enter để quay lại menu...")
            
            elif choice == "3":
                self.clear_screen()
                self.print_banner()
                if not self.repo_path:
                    self.repo_path = input("\n📁 Đường dẫn thư mục: ").strip() or os.getcwd()
                self.create_gitignore()
                input("\n✅ Nhấn Enter để quay lại menu...")
            
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
                    print("\n⚠️  Đang dừng tự động upload...")
                    self.auto_upload_running = False
                    if self.auto_upload_thread:
                        self.auto_upload_thread.join(timeout=5)
                
                self.logger.info("Tool đã đóng")
                self.logger.info("=" * 60)
                print("\n👋 Cảm ơn bạn đã sử dụng! Tạm biệt!")
                break
            
            else:
                print("❌ Lựa chọn không hợp lệ!")
                input("\n✅ Nhấn Enter để thử lại...")

def main():
    try:
        uploader = GitHubUploader()
        uploader.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Đã dừng chương trình!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
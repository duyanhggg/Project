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


class GitHubUploader:
    def __init__(self):
        # Default to current working directory; can be adjusted later
        self.repo_path = os.getcwd()
        self.repo_url = None
        self.branch = "main"

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
            return result.returncode == 0, (result.stdout or "").strip(), (result.stderr or "").strip()
        except Exception as e:
            return False, "", str(e)

    def _git(self, args: str):
        return self.run_command(f'git -C "{self.repo_path}" {args}')

    def init_git_repo(self) -> bool:
        ok, out, err = self._git("rev-parse --is-inside-work-tree")
        if ok and out.strip() == "true":
            return True
        ok, _, _ = self._git("init")
        return ok

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

    # Placeholders for menu items not wired into this minimal GUI
    def manage_saved_configs(self):
        messagebox.showinfo("Configs", "This simplified GUI does not support saved configs yet.")

    def start_auto_upload(self):
        messagebox.showinfo("Auto Upload", "Background auto-upload not implemented in this minimal GUI.")

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
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill='both')

        logo = tk.PhotoImage(width=1, height=1)  # Placeholder image
        ttk.Label(frame, text="GitHub Auto Upload Tool Pro", style='TLabel').pack(pady=(0, 12))

        ttk.Button(frame, text="[UPLOAD] Upload code lên GitHub", image=logo, compound='left', command=self.upload_code).pack(fill='x', pady=6)
        ttk.Button(frame, text="[STATUS] Xem trạng thái Git", image=logo, compound='left', command=self.show_git_status).pack(fill='x', pady=6)
        ttk.Button(frame, text="[EDIT] Tạo/Sửa .gitignore", image=logo, compound='left', command=self.create_gitignore).pack(fill='x', pady=6)
        ttk.Button(frame, text="[CONFIG] Quản lý cấu hình đã lưu", image=logo, compound='left', command=self.manage_saved_configs).pack(fill='x', pady=6)
        ttk.Button(frame, text="[TIME] Cấu hình tự động upload", image=logo, compound='left', command=self.configure_auto_upload).pack(fill='x', pady=6)
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

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    import sys, os, subprocess, logging
    uploader = GitHubUploader()
    gui = GitHubUploaderGUI(uploader)
    gui.run()

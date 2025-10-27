#!/usr/bin/env python3
"""
build_exe.py
Small helper to package a Python script into a single-file Windows executable using PyInstaller.
Usage:
    python build_exe.py [path/to/script.pyw] [--icon images.ico] [--no-clean]
"""
import os
import sys
import subprocess
import shutil
import logging
import argparse

def ensure_pyinstaller():
    try:
        import PyInstaller  # noqa: F401
    except Exception:
        logging.info("PyInstaller not found, installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def clean_previous(script_path):
    base = os.path.splitext(os.path.basename(script_path))[0]
    for name in ("build", "dist", f"{base}.spec"):
        if os.path.exists(name):
            if os.path.isdir(name):
                shutil.rmtree(name)
            else:
                os.remove(name)

def build_exe(script_path, icon=None, onefile=True, windowed=True, hidden_imports=None, add_datas=None):
    script_path = os.path.abspath(script_path)
    if not os.path.exists(script_path):
        logging.error("Script not found: %s", script_path)
        raise SystemExit(1)

    cmd = [sys.executable, "-m", "PyInstaller"]
    if onefile:
        cmd.append("--onefile")
    if windowed:
        cmd.append("--windowed")
    if icon:
        cmd.extend(["--icon", icon])
    if hidden_imports:
        for hi in hidden_imports:
            cmd.extend(["--hidden-import", hi])
    if add_datas:
        for src, dst in add_datas:
            # PyInstaller expects path separator on Windows; os.pathsep works cross-platform
            cmd.extend(["--add-data", f"{src}{os.pathsep}{dst}"])
    cmd.append(script_path)

    logging.info("Running PyInstaller...")
    logging.debug("Command: %s", " ".join(cmd))
    subprocess.check_call(cmd)

def main():
    parser = argparse.ArgumentParser(description="Package a Python script into an executable using PyInstaller.")
    parser.add_argument("script", nargs="?", default="file.pyw", help="Script to package (default: file.pyw).")
    parser.add_argument("--icon", default="images.ico", help="Path to .ico file to embed (default: images.ico).")
    parser.add_argument("--no-clean", dest="clean", action="store_false", help="Do not remove previous build artifacts.")
    parser.add_argument("--name", dest="exe_name", default=None, help="Name of the output executable (without .exe).")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ensure_pyinstaller()

    script_path = args.script
    icon_path = args.icon if os.path.exists(args.icon) else None

    if args.clean:
        clean_previous(script_path)

    # Common hidden imports for this project (add win10toast and plyer windows backends)
    hidden = [
        "infi.systray",
        "plyer",
        "plyer.platforms.win.notification",
        "plyer.platforms.win.toast",
        "win32com",
        "winshell",
        "win10toast"
    ]
    # Add data files if needed, e.g., ("images.ico", ".")
    add_datas = []
    try:
        # pass name to PyInstaller if provided
        build_exe(
            script_path,
            icon=icon_path,
            onefile=True,
            windowed=True,
            hidden_imports=hidden,
            add_datas=add_datas,
        )
        # rename resulting exe if user passed --name (dist/<orig>.exe -> dist/<name>.exe)
        if args.exe_name:
            base = os.path.splitext(os.path.basename(script_path))[0]
            src = os.path.join("dist", f"{base}.exe")
            dst = os.path.join("dist", f"{args.exe_name}.exe")
            if os.path.exists(src):
                shutil.move(src, dst)
        logging.info("Build completed successfully. See the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        logging.error("PyInstaller failed with exit code %s", e.returncode)
        raise SystemExit(e.returncode)

if __name__ == "__main__":
    main()
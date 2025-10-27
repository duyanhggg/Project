"""Create Windows shortcut (.lnk) in user's startup folder.

Usage:
    python create_shortcut.py --target "C:\\path\\to\\pythonw.exe" --script "C:\\path\\to\\run_update_gui.pyw" --name "GitHub Auto Upload"

This script is safe to call on Windows only; it will attempt to create a shortcut in the current user's startup folder.
"""
import os
import sys
import argparse

def create_shortcut(target, script, name, args=''):
    try:
        from win32com.client import Dispatch
    except Exception as e:
        print('win32com is required to create shortcuts on Windows. Install pywin32.')
        raise

    startup = os.path.join(os.environ.get('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    os.makedirs(startup, exist_ok=True)
    shortcut_path = os.path.join(startup, f"{name}.lnk")

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target
    shortcut.Arguments = f'"{script}" {args}' if args else f'"{script}"'
    shortcut.WorkingDirectory = os.path.dirname(script)
    shortcut.IconLocation = target
    shortcut.save()
    print(f'Created shortcut: {shortcut_path}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', help='Executable to run (pythonw.exe recommended)', required=True)
    parser.add_argument('--script', help='Script to pass as argument to the executable', required=True)
    parser.add_argument('--name', help='Name of the shortcut', required=True)
    parser.add_argument('--args', help='Additional arguments', default='')
    args = parser.parse_args()

    if os.name != 'nt':
        print('This helper only runs on Windows.')
        sys.exit(2)

    create_shortcut(args.target, args.script, args.name, args.args)


if __name__ == '__main__':
    main()

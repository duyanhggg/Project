import os
import sqlite3
import tempfile
import sys
import importlib.util

# Ensure we can import main.py as a module
PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import main


def test_create_demo_db_and_table_exists():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    try:
        if os.path.exists(path):
            os.remove(path)
        main.create_demo_db(path)
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items'")
        rows = cur.fetchall()
        conn.close()
        assert len(rows) == 1
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_sort_table_outside_and_order_desc():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    try:
        if os.path.exists(path):
            os.remove(path)
        main.create_demo_db(path)
        out = main.sort_table(path, "items", column="value", order="desc", inplace=False)
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute(f"SELECT value FROM {out} LIMIT 1")
        first = cur.fetchone()[0]
        conn.close()
        assert first == 5.0
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_sort_table_inplace_by_name():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    try:
        if os.path.exists(path):
            os.remove(path)
        main.create_demo_db(path)
        main.sort_table(path, "items", column="name", order="asc", inplace=True)
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM items LIMIT 1")
        first = cur.fetchone()[0]
        conn.close()
        # names are: banana, apple, carrot, eggplant, date -> sorted asc -> apple first
        assert first == "apple"
    finally:
        if os.path.exists(path):
            os.remove(path)

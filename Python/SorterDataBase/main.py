"""Simple SQLite table sorter CLI

Usage examples:
  - Create demo DB and show sorting demo:
	  python main.py --demo
  - Sort table by a specific column into a new table:
	  python main.py --db data.db --table items --column value --order desc --output items_sorted
  - Sort table in-place:
	  python main.py --db data.db --table items --column name --inplace

The script infers a sortable column if none is provided (prefers numeric columns).
"""
from __future__ import annotations

import argparse
import logging
import os
import sqlite3
import sys
from typing import List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("sorter")


def create_demo_db(path: str) -> None:
	"""Create a small demo DB with unsorted rows."""
	if os.path.exists(path):
		os.remove(path)
	conn = sqlite3.connect(path)
	cur = conn.cursor()
	cur.execute(
		"""
		CREATE TABLE items (
			id INTEGER PRIMARY KEY,
			name TEXT,
			value REAL,
			category TEXT
		)
		"""
	)
	rows = [
		(1, "banana", 2.5, "fruit"),
		(2, "apple", 5.0, "fruit"),
		(3, "carrot", 1.2, "veg"),
		(4, "eggplant", 3.1, "veg"),
		(5, "date", 4.0, "fruit"),
	]
	cur.executemany("INSERT INTO items(id,name,value,category) VALUES (?,?,?,?)", rows)
	conn.commit()
	conn.close()
	logger.info(f"Created demo DB at {path} with table 'items'")


def list_tables(conn: sqlite3.Connection) -> List[str]:
	cur = conn.cursor()
	cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
	return [r[0] for r in cur.fetchall()]


def get_table_columns(conn: sqlite3.Connection, table: str) -> List[Tuple[str, str]]:
	"""Return list of (name, type) from PRAGMA table_info."""
	cur = conn.cursor()
	cur.execute(f"PRAGMA table_info('{table}')")
	rows = cur.fetchall()
	return [(r[1], r[2]) for r in rows]


def infer_sortable_column(conn: sqlite3.Connection, table: str) -> Optional[str]:
	"""Pick a reasonable column to sort by: prefer numeric, else text first column."""
	cols = get_table_columns(conn, table)
	if not cols:
		return None
	# prefer numeric types
	for name, ctype in cols:
		if ctype and any(k in ctype.upper() for k in ("INT", "REAL", "NUM", "DECIMAL", "FLOAT")):
			return name
	# fallback to first text column
	for name, ctype in cols:
		return name
	return None


def ensure_unique_table_name(conn: sqlite3.Connection, base: str) -> str:
	cur = conn.cursor()
	exists = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
	if base not in exists:
		return base
	i = 1
	while f"{base}_{i}" in exists:
		i += 1
	return f"{base}_{i}"


def sort_table(
	db_path: str,
	table: str,
	column: Optional[str] = None,
	order: str = "asc",
	output: Optional[str] = None,
	inplace: bool = False,
) -> str:
	"""Sort a table in SQLite and return the name of the table with sorted data.

	If inplace is False the sorted rows are written to `output` (or table_sorted by default).
	If inplace is True the original table is replaced atomically.
	"""
	if order.lower() not in ("asc", "desc"):
		raise ValueError("order must be 'asc' or 'desc'")

	conn = sqlite3.connect(db_path)
	cur = conn.cursor()

	tables = list_tables(conn)
	if table not in tables:
		conn.close()
		raise ValueError(f"Table '{table}' does not exist in database")

	cols = [c for c, _ in get_table_columns(conn, table)]
	if not cols:
		conn.close()
		raise ValueError(f"Table '{table}' has no columns")

	if column is None:
		column = infer_sortable_column(conn, table)
		if column is None:
			conn.close()
			raise ValueError("Could not infer a sortable column; please specify --column")
		logger.info(f"Inferred column '{column}' to sort by")

	if column not in cols:
		conn.close()
		raise ValueError(f"Column '{column}' does not exist in table '{table}'")

	order_sql = "ASC" if order.lower() == "asc" else "DESC"

	# Build safe ORDER BY - prefer numeric sort when column affinity is numeric
	# SQLite allows CAST(... AS REAL) to coerce
	col_types = dict(get_table_columns(conn, table))
	ctype = (col_types.get(column) or "").upper()
	if any(k in ctype for k in ("INT", "REAL", "NUM", "FLOAT", "DECIMAL")):
		order_by = f"CAST({column} AS REAL) {order_sql}"
	else:
		# text col: use COLLATE NOCASE for more friendly ordering
		order_by = f"{column} COLLATE NOCASE {order_sql}"

	if inplace:
		tmp = ensure_unique_table_name(conn, f"{table}_tmp_sorted")
		sql = f"CREATE TABLE {tmp} AS SELECT * FROM {table} ORDER BY {order_by};"
		logger.info(f"Creating temporary sorted table '{tmp}'")
		cur.execute(sql)
		conn.commit()
		logger.info(f"Dropping original table '{table}' and renaming '{tmp}' -> '{table}'")
		cur.execute(f"DROP TABLE {table}")
		cur.execute(f"ALTER TABLE {tmp} RENAME TO {table}")
		conn.commit()
		conn.close()
		return table
	else:
		out_name = output or f"{table}_sorted"
		out_name = ensure_unique_table_name(conn, out_name)
		sql = f"CREATE TABLE {out_name} AS SELECT * FROM {table} ORDER BY {order_by};"
		logger.info(f"Creating sorted table '{out_name}'")
		cur.execute(sql)
		conn.commit()
		conn.close()
		return out_name


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Sort a table in a SQLite database")
	p.add_argument("--db", help="Path to sqlite database (if omitted you will be prompted)", default=None)
	p.add_argument("--ask-db", help="Force prompting for DB path (even if non-interactive)", action="store_true")
	p.add_argument("--table", help="Table name to sort")
	p.add_argument("--column", help="Column to sort by (optional)")
	p.add_argument("--order", help="asc or desc", choices=("asc", "desc"), default="asc")
	p.add_argument("--inplace", help="Replace the original table", action="store_true")
	p.add_argument("--output", help="Output table name (when not in-place)")
	p.add_argument("--demo", help="Create demo DB and run sample sort", action="store_true")
	return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
	args = parse_args(argv)

	if args.demo:
		db = os.path.join(os.path.dirname(__file__), "demo_db.sqlite")
		create_demo_db(db)
		# show before
		conn = sqlite3.connect(db)
		cur = conn.cursor()
		logger.info("Before sorting:")
		for row in cur.execute("SELECT * FROM items"):
			logger.info(row)
		conn.close()
		out = sort_table(db, "items", column=None, order="asc", inplace=False)
		conn = sqlite3.connect(db)
		cur = conn.cursor()
		logger.info(f"After sorting into table '{out}':")
		for row in cur.execute(f"SELECT * FROM {out}"):
			logger.info(row)
		conn.close()
		logger.info("Demo complete")
		return 0

	# ensure we have a database path; if not provided, prompt the user.
	db_path = args.db
	if not db_path:
		# If ask-db is set, we attempt to prompt even when stdin isn't a TTY.
		if not args.ask_db and (sys.stdin is None or not sys.stdin.isatty()):
			logger.error("--db is required when not running --demo (non-interactive). Use --ask-db to attempt prompting.")
			return 2
		try:
			# This may raise EOFError in non-interactive contexts; that's fine and will be handled.
			db_path = input("Enter path to sqlite database: ").strip()
		except (EOFError, KeyboardInterrupt):
			logger.error("No database path provided")
			return 2
		if not db_path:
			logger.error("Empty database path")
			return 2

	if not args.table:
		logger.error("--table is required when not running --demo")
		return 2

	try:
		output_table = sort_table(
			db_path, args.table, column=args.column, order=args.order, output=args.output, inplace=args.inplace
		)
		logger.info(f"Sorted table available at: {output_table}")
		return 0
	except Exception as e:
		logger.error(f"Error: {e}")
		return 1


if __name__ == "__main__":
	raise SystemExit(main())


SQLite Table Sorter

This small CLI sorts tables inside a SQLite database.

Usage examples:

- Create demo DB and show sorting demo:

  python main.py --demo

- Sort table into a new table (auto name if exists):

  python main.py --db path\to\data.db --table items --column value --order desc --output items_sorted

- Sort table in-place (replace original table):

  python main.py --db path\to\data.db --table items --column name --inplace

- Omit `--db` to be prompted interactively (only works in a terminal):

  python main.py --table items

- Force prompting for DB path even in non-interactive contexts (may fail if stdin closed):

  python main.py --ask-db --table items

Notes

- If `--column` is omitted the script attempts to infer a sortable column (prefers numeric types).
- For numeric-affinity columns sorting uses CAST(... AS REAL). For text it uses case-insensitive collation.
- In-place replacement is implemented by creating a temporary sorted table and renaming it; be careful with concurrent connections.

Next steps

- Add tests and CI if you want automated verification.

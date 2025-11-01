"""
Advanced Database Manager Pro
Hỗ trợ: SQLite, MySQL, PostgreSQL, MongoDB
Tính năng: GUI hiện đại, Filter nâng cao, Sort đa cấp, Export đa định dạng, SQL Editor
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd
import sqlite3
from typing import List, Dict, Optional, Any, Tuple
import json
from datetime import datetime
import threading

# Import tùy chọn cho các database khác
try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False


class DatabaseConnector:
    """Lớp kết nối đến các loại database khác nhau"""
    
    def __init__(self, db_type: str, **kwargs):
        self.db_type = db_type
        self.connection = None
        self.kwargs = kwargs
        
    def connect(self) -> Tuple[bool, str]:
        """Kết nối đến database"""
        try:
            if self.db_type == 'sqlite':
                self.connection = sqlite3.connect(self.kwargs.get('path', 'database.db'))
                return True, "Kết nối SQLite thành công"
                
            elif self.db_type == 'mysql' and MYSQL_AVAILABLE:
                self.connection = pymysql.connect(
                    host=self.kwargs.get('host', 'localhost'),
                    user=self.kwargs.get('user', 'root'),
                    password=self.kwargs.get('password', ''),
                    database=self.kwargs.get('database', ''),
                    port=self.kwargs.get('port', 3306)
                )
                return True, "Kết nối MySQL thành công"
                
            elif self.db_type == 'postgresql' and POSTGRES_AVAILABLE:
                self.connection = psycopg2.connect(
                    host=self.kwargs.get('host', 'localhost'),
                    user=self.kwargs.get('user', 'postgres'),
                    password=self.kwargs.get('password', ''),
                    database=self.kwargs.get('database', ''),
                    port=self.kwargs.get('port', 5432)
                )
                return True, "Kết nối PostgreSQL thành công"
                
            elif self.db_type == 'mongodb' and MONGO_AVAILABLE:
                uri = self.kwargs.get('uri', 'mongodb://localhost:27017/')
                client = MongoClient(uri, serverSelectionTimeoutMS=5000)
                client.server_info()  # Test connection
                db_name = self.kwargs.get('database', 'test')
                self.connection = client[db_name]
                return True, "Kết nối MongoDB thành công"
            else:
                return False, f"Database {self.db_type} không được hỗ trợ hoặc thiếu thư viện"
                
        except Exception as e:
            return False, f"Lỗi kết nối: {str(e)}"
    
    def get_tables(self) -> List[str]:
        """Lấy danh sách bảng/collection"""
        try:
            if self.db_type == 'mongodb':
                return sorted(self.connection.list_collection_names())
            else:
                if self.db_type == 'sqlite':
                    query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
                elif self.db_type == 'mysql':
                    query = "SHOW TABLES;"
                elif self.db_type == 'postgresql':
                    query = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public';"
                
                cursor = self.connection.cursor()
                cursor.execute(query)
                return sorted([row[0] for row in cursor.fetchall()])
        except Exception as e:
            raise Exception(f"Lỗi lấy danh sách bảng: {str(e)}")
    
    def get_columns(self, table_name: str) -> List[str]:
        """Lấy danh sách cột"""
        try:
            if self.db_type == 'mongodb':
                collection = self.connection[table_name]
                sample = collection.find_one()
                return list(sample.keys()) if sample else []
            else:
                if self.db_type == 'sqlite':
                    query = f"PRAGMA table_info({table_name});"
                    cursor = self.connection.cursor()
                    cursor.execute(query)
                    return [row[1] for row in cursor.fetchall()]
                else:
                    cursor = self.connection.cursor()
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    return [desc[0] for desc in cursor.description]
        except Exception as e:
            raise Exception(f"Lỗi lấy cột: {str(e)}")
    
    def get_row_count(self, table_name: str, filters: Dict = None) -> int:
        """Đếm số dòng"""
        try:
            if self.db_type == 'mongodb':
                collection = self.connection[table_name]
                mongo_filter = self._build_mongo_filter(filters) if filters else {}
                return collection.count_documents(mongo_filter)
            else:
                query = f"SELECT COUNT(*) FROM {table_name}"
                if filters:
                    where_parts = self._build_where_clause(filters)
                    if where_parts:
                        query += " WHERE " + " AND ".join(where_parts)
                cursor = self.connection.cursor()
                cursor.execute(query)
                return cursor.fetchone()[0]
        except Exception as e:
            return 0
    
    def _build_mongo_filter(self, filters: Dict) -> Dict:
        """Xây dựng MongoDB filter"""
        mongo_filter = {}
        for col, (op, val) in filters.items():
            if op == '=':
                mongo_filter[col] = val
            elif op == '!=':
                mongo_filter[col] = {'$ne': val}
            elif op == '>':
                mongo_filter[col] = {'$gt': val}
            elif op == '<':
                mongo_filter[col] = {'$lt': val}
            elif op == '>=':
                mongo_filter[col] = {'$gte': val}
            elif op == '<=':
                mongo_filter[col] = {'$lte': val}
            elif op == 'LIKE':
                mongo_filter[col] = {'$regex': val.replace('%', '.*'), '$options': 'i'}
        return mongo_filter
    
    def _build_where_clause(self, filters: Dict) -> List[str]:
        """Xây dựng WHERE clause cho SQL"""
        where_parts = []
        for col, (op, val) in filters.items():
            if isinstance(val, str):
                val_escaped = val.replace("'", "''")
                where_parts.append(f"{col} {op} '{val_escaped}'")
            else:
                where_parts.append(f"{col} {op} {val}")
        return where_parts
    
    def query_data(self, table_name: str, filters: Dict = None, 
                   sort_columns: List[str] = None, ascending: List[bool] = None,
                   limit: int = None, offset: int = 0) -> pd.DataFrame:
        """Truy vấn dữ liệu với filter và sort"""
        
        if self.db_type == 'mongodb':
            collection = self.connection[table_name]
            
            mongo_filter = self._build_mongo_filter(filters) if filters else {}
            
            mongo_sort = []
            if sort_columns:
                for col, asc in zip(sort_columns, ascending or [True]*len(sort_columns)):
                    mongo_sort.append((col, 1 if asc else -1))
            
            cursor = collection.find(mongo_filter)
            if mongo_sort:
                cursor = cursor.sort(mongo_sort)
            if offset:
                cursor = cursor.skip(offset)
            if limit:
                cursor = cursor.limit(limit)
            
            data = list(cursor)
            return pd.DataFrame(data)
            
        else:
            query = f"SELECT * FROM {table_name}"
            
            if filters:
                where_parts = self._build_where_clause(filters)
                if where_parts:
                    query += " WHERE " + " AND ".join(where_parts)
            
            if sort_columns:
                order_parts = []
                for col, asc in zip(sort_columns, ascending or [True]*len(sort_columns)):
                    direction = "ASC" if asc else "DESC"
                    order_parts.append(f"{col} {direction}")
                query += " ORDER BY " + ", ".join(order_parts)
            
            if limit:
                query += f" LIMIT {limit}"
            if offset:
                query += f" OFFSET {offset}"
            
            return pd.read_sql_query(query, self.connection)
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Thực thi SQL query tùy chỉnh"""
        if self.db_type == 'mongodb':
            raise Exception("MongoDB không hỗ trợ SQL query")
        return pd.read_sql_query(query, self.connection)
    
    def close(self):
        """Đóng kết nối"""
        if self.connection:
            if self.db_type == 'mongodb':
                self.connection.client.close()
            else:
                self.connection.close()


class ModernStyle:
    """Định nghĩa style hiện đại cho ứng dụng"""
    
    # Colors
    BG_PRIMARY = "#1e1e2e"
    BG_SECONDARY = "#2d2d44"
    BG_TERTIARY = "#3d3d5c"
    FG_PRIMARY = "#cdd6f4"
    FG_SECONDARY = "#a6adc8"
    ACCENT_BLUE = "#89b4fa"
    ACCENT_GREEN = "#a6e3a1"
    ACCENT_RED = "#f38ba8"
    ACCENT_YELLOW = "#f9e2af"
    ACCENT_PURPLE = "#cba6f7"
    
    @staticmethod
    def apply_style():
        """Áp dụng style cho ttk widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('.',
                       background=ModernStyle.BG_PRIMARY,
                       foreground=ModernStyle.FG_PRIMARY,
                       fieldbackground=ModernStyle.BG_SECONDARY,
                       bordercolor=ModernStyle.BG_TERTIARY,
                       darkcolor=ModernStyle.BG_SECONDARY,
                       lightcolor=ModernStyle.BG_TERTIARY)
        
        # Frame
        style.configure('TFrame', background=ModernStyle.BG_PRIMARY)
        style.configure('Card.TFrame', background=ModernStyle.BG_SECONDARY, relief='raised')
        
        # LabelFrame
        style.configure('TLabelframe', 
                       background=ModernStyle.BG_PRIMARY,
                       foreground=ModernStyle.ACCENT_BLUE,
                       bordercolor=ModernStyle.ACCENT_BLUE)
        style.configure('TLabelframe.Label',
                       background=ModernStyle.BG_PRIMARY,
                       foreground=ModernStyle.ACCENT_BLUE,
                       font=('Segoe UI', 10, 'bold'))
        
        # Label
        style.configure('TLabel',
                       background=ModernStyle.BG_PRIMARY,
                       foreground=ModernStyle.FG_PRIMARY)
        style.configure('Title.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       foreground=ModernStyle.ACCENT_BLUE)
        
        # Button
        style.configure('TButton',
                       background=ModernStyle.ACCENT_BLUE,
                       foreground='#1e1e2e',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 9))
        style.map('TButton',
                 background=[('active', ModernStyle.ACCENT_PURPLE)])
        
        style.configure('Success.TButton',
                       background=ModernStyle.ACCENT_GREEN)
        style.configure('Danger.TButton',
                       background=ModernStyle.ACCENT_RED)
        style.configure('Warning.TButton',
                       background=ModernStyle.ACCENT_YELLOW)
        
        # Entry
        style.configure('TEntry',
                       fieldbackground=ModernStyle.BG_SECONDARY,
                       foreground=ModernStyle.FG_PRIMARY,
                       bordercolor=ModernStyle.BG_TERTIARY,
                       insertcolor=ModernStyle.FG_PRIMARY)
        
        # Combobox
        style.configure('TCombobox',
                       fieldbackground=ModernStyle.BG_SECONDARY,
                       background=ModernStyle.BG_SECONDARY,
                       foreground=ModernStyle.FG_PRIMARY,
                       arrowcolor=ModernStyle.ACCENT_BLUE)
        
        # Treeview
        style.configure('Treeview',
                       background=ModernStyle.BG_SECONDARY,
                       foreground=ModernStyle.FG_PRIMARY,
                       fieldbackground=ModernStyle.BG_SECONDARY,
                       borderwidth=0,
                       font=('Segoe UI', 9))
        style.configure('Treeview.Heading',
                       background=ModernStyle.BG_TERTIARY,
                       foreground=ModernStyle.ACCENT_BLUE,
                       borderwidth=1,
                       font=('Segoe UI', 9, 'bold'))
        style.map('Treeview',
                 background=[('selected', ModernStyle.ACCENT_BLUE)],
                 foreground=[('selected', '#1e1e2e')])
        
        # Notebook
        style.configure('TNotebook',
                       background=ModernStyle.BG_PRIMARY,
                       borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=ModernStyle.BG_SECONDARY,
                       foreground=ModernStyle.FG_SECONDARY,
                       padding=[20, 10],
                       font=('Segoe UI', 9))
        style.map('TNotebook.Tab',
                 background=[('selected', ModernStyle.BG_TERTIARY)],
                 foreground=[('selected', ModernStyle.ACCENT_BLUE)])


class DatabaseSortGUI:
    """Giao diện GUI hiện đại cho Database Manager"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🗄️ Database Manager Pro")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        
        # Apply modern style
        ModernStyle.apply_style()
        self.root.configure(bg=ModernStyle.BG_PRIMARY)
        
        self.connector = None
        self.current_table = None
        self.filters = {}
        self.current_df = None
        self.pagination_offset = 0
        self.pagination_limit = 100
        
        self.setup_ui()
        self.center_window()
    
    def center_window(self):
        """Căn giữa cửa sổ"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        
        # Main container
        main_container = ttk.Frame(self.root, style='TFrame')
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self.setup_header(main_container)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True, pady=(10, 0))
        
        # Tab 1: Query Builder
        self.query_tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.query_tab, text="📊 Query Builder")
        self.setup_query_tab()
        
        # Tab 2: SQL Editor
        self.sql_tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.sql_tab, text="💻 SQL Editor")
        self.setup_sql_tab()
        
        # Tab 3: Connection Manager
        self.conn_tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.conn_tab, text="🔌 Connections")
        self.setup_connection_tab()
        
        # Status bar
        self.setup_status_bar(main_container)
    
    def setup_header(self, parent):
        """Thiết lập header"""
        header = ttk.Frame(parent, style='Card.TFrame')
        header.pack(fill="x", pady=(0, 10))
        
        title_label = ttk.Label(header, text="🗄️ Database Manager Pro",
                               style='Title.TLabel',
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(side="left", padx=20, pady=15)
        
        # Connection status
        self.conn_status = ttk.Label(header, text="⚫ Disconnected",
                                    foreground=ModernStyle.ACCENT_RED)
        self.conn_status.pack(side="right", padx=20, pady=15)
    
    def setup_query_tab(self):
        """Thiết lập tab Query Builder"""
        
        # Paned window
        paned = ttk.PanedWindow(self.query_tab, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel
        left_panel = ttk.Frame(paned, style='TFrame')
        paned.add(left_panel, weight=1)
        
        # Tables section
        tables_frame = ttk.LabelFrame(left_panel, text="📁 Tables", padding=10)
        tables_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Search box
        search_frame = ttk.Frame(tables_frame)
        search_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(search_frame, text="🔍").pack(side="left", padx=(0, 5))
        self.table_search_var = tk.StringVar()
        self.table_search_var.trace('w', self.filter_tables)
        search_entry = ttk.Entry(search_frame, textvariable=self.table_search_var)
        search_entry.pack(fill="x", expand=True)
        
        # Table listbox with scrollbar
        table_scroll = ttk.Scrollbar(tables_frame)
        table_scroll.pack(side="right", fill="y")
        
        self.table_listbox = tk.Listbox(tables_frame, 
                                        bg=ModernStyle.BG_SECONDARY,
                                        fg=ModernStyle.FG_PRIMARY,
                                        selectbackground=ModernStyle.ACCENT_BLUE,
                                        selectforeground='#1e1e2e',
                                        yscrollcommand=table_scroll.set,
                                        font=('Segoe UI', 9),
                                        borderwidth=0,
                                        highlightthickness=0)
        self.table_listbox.pack(fill="both", expand=True)
        table_scroll.config(command=self.table_listbox.yview)
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        
        # Columns section
        columns_frame = ttk.LabelFrame(left_panel, text="📋 Columns", padding=10)
        columns_frame.pack(fill="both", expand=True)
        
        col_scroll = ttk.Scrollbar(columns_frame)
        col_scroll.pack(side="right", fill="y")
        
        self.column_listbox = tk.Listbox(columns_frame, 
                                         bg=ModernStyle.BG_SECONDARY,
                                         fg=ModernStyle.FG_PRIMARY,
                                         selectbackground=ModernStyle.ACCENT_BLUE,
                                         selectforeground='#1e1e2e',
                                         selectmode="extended",
                                         yscrollcommand=col_scroll.set,
                                         font=('Segoe UI', 9),
                                         borderwidth=0,
                                         highlightthickness=0)
        self.column_listbox.pack(fill="both", expand=True)
        col_scroll.config(command=self.column_listbox.yview)
        
        # Right panel
        right_panel = ttk.Frame(paned, style='TFrame')
        paned.add(right_panel, weight=2)
        
        # Filter section
        self.setup_filter_section(right_panel)
        
        # Sort section
        self.setup_sort_section(right_panel)
        
        # Action buttons
        self.setup_action_buttons(right_panel)
        
        # Results section
        self.setup_results_section(right_panel)
    
    def setup_filter_section(self, parent):
        """Thiết lập phần filter"""
        filter_frame = ttk.LabelFrame(parent, text="🔍 Filters", padding=10)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # Filter controls
        ctrl_frame = ttk.Frame(filter_frame)
        ctrl_frame.pack(fill="x", pady=(0, 10))
        
        # Column
        ttk.Label(ctrl_frame, text="Column:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.filter_column_var = tk.StringVar()
        self.filter_column_combo = ttk.Combobox(ctrl_frame, textvariable=self.filter_column_var, 
                                               width=15, state='readonly')
        self.filter_column_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Operator
        ttk.Label(ctrl_frame, text="Operator:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.filter_op_var = tk.StringVar(value='=')
        ttk.Combobox(ctrl_frame, textvariable=self.filter_op_var, 
                    values=['=', '!=', '>', '<', '>=', '<=', 'LIKE'], 
                    width=8, state='readonly').grid(row=0, column=3, padx=5, pady=5)
        
        # Value
        ttk.Label(ctrl_frame, text="Value:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.filter_value_var = tk.StringVar()
        ttk.Entry(ctrl_frame, textvariable=self.filter_value_var, 
                 width=20).grid(row=0, column=5, padx=5, pady=5)
        
        # Buttons
        ttk.Button(ctrl_frame, text="➕ Add", 
                  command=self.add_filter, 
                  style='Success.TButton').grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(ctrl_frame, text="🗑️ Clear All", 
                  command=self.clear_filters,
                  style='Danger.TButton').grid(row=0, column=7, padx=5, pady=5)
        
        # Filter display
        filter_display_frame = ttk.Frame(filter_frame)
        filter_display_frame.pack(fill="both", expand=True)
        
        filter_scroll = ttk.Scrollbar(filter_display_frame)
        filter_scroll.pack(side="right", fill="y")
        
        self.filter_text = tk.Text(filter_display_frame,
                                   height=4,
                                   bg=ModernStyle.BG_SECONDARY,
                                   fg=ModernStyle.FG_PRIMARY,
                                   insertbackground=ModernStyle.FG_PRIMARY,
                                   font=('Consolas', 9),
                                   yscrollcommand=filter_scroll.set,
                                   borderwidth=0,
                                   highlightthickness=1,
                                   highlightbackground=ModernStyle.BG_TERTIARY)
        self.filter_text.pack(fill="both", expand=True)
        filter_scroll.config(command=self.filter_text.yview)
        self.filter_text.config(state='disabled')
    
    def setup_sort_section(self, parent):
        """Thiết lập phần sort"""
        sort_frame = ttk.LabelFrame(parent, text="🔽 Sort Order", padding=10)
        sort_frame.pack(fill="x", pady=(0, 10))
        
        sort_container = ttk.Frame(sort_frame)
        sort_container.pack(fill="x")
        
        # Sort listbox
        sort_list_frame = ttk.Frame(sort_container)
        sort_list_frame.pack(side="left", fill="both", expand=True)
        
        sort_scroll = ttk.Scrollbar(sort_list_frame)
        sort_scroll.pack(side="right", fill="y")
        
        self.sort_listbox = tk.Listbox(sort_list_frame,
                                       height=4,
                                       bg=ModernStyle.BG_SECONDARY,
                                       fg=ModernStyle.FG_PRIMARY,
                                       selectbackground=ModernStyle.ACCENT_BLUE,
                                       selectforeground='#1e1e2e',
                                       yscrollcommand=sort_scroll.set,
                                       font=('Segoe UI', 9),
                                       borderwidth=0,
                                       highlightthickness=1,
                                       highlightbackground=ModernStyle.BG_TERTIARY)
        self.sort_listbox.pack(fill="both", expand=True)
        sort_scroll.config(command=self.sort_listbox.yview)
        
        # Sort buttons
        sort_btn_frame = ttk.Frame(sort_container)
        sort_btn_frame.pack(side="left", fill="y", padx=(10, 0))
        
        ttk.Button(sort_btn_frame, text="⬆️ ASC", 
                  command=self.add_sort_asc, width=10).pack(pady=2)
        ttk.Button(sort_btn_frame, text="⬇️ DESC", 
                  command=self.add_sort_desc, width=10).pack(pady=2)
        ttk.Button(sort_btn_frame, text="❌ Remove", 
                  command=self.remove_sort, width=10).pack(pady=2)
        ttk.Button(sort_btn_frame, text="🗑️ Clear", 
                  command=self.clear_sorts, 
                  style='Danger.TButton', width=10).pack(pady=2)
    
    def setup_action_buttons(self, parent):
        """Thiết lập nút action"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill="x", pady=(0, 10))
        
        # Left side - Query options
        left_actions = ttk.Frame(action_frame)
        left_actions.pack(side="left", fill="x", expand=True)
        
        ttk.Label(left_actions, text="Limit:").pack(side="left", padx=5)
        self.limit_var = tk.StringVar(value="100")
        ttk.Combobox(left_actions, textvariable=self.limit_var,
                    values=['10', '50', '100', '500', '1000', '5000', 'All'],
                    width=8, state='readonly').pack(side="left", padx=5)
        
        ttk.Button(left_actions, text="🔄 Refresh Tables",
                  command=self.refresh_tables).pack(side="left", padx=5)
        
        # Right side - Action buttons
        right_actions = ttk.Frame(action_frame)
        right_actions.pack(side="right")
        
        ttk.Button(right_actions, text="🔍 Query",
                  command=self.view_data,
                  style='Success.TButton').pack(side="left", padx=5)
        ttk.Button(right_actions, text="💾 Export CSV",
                  command=self.export_csv).pack(side="left", padx=5)
        ttk.Button(right_actions, text="📊 Export Excel",
                  command=self.export_excel).pack(side="left", padx=5)
        ttk.Button(right_actions, text="📋 Export JSON",
                  command=self.export_json).pack(side="left", padx=5)
    
    def setup_results_section(self, parent):
        """Thiết lập phần hiển thị kết quả"""
        result_frame = ttk.LabelFrame(parent, text="📋 Results", padding=10)
        result_frame.pack(fill="both", expand=True)
        
        # Toolbar
        toolbar = ttk.Frame(result_frame)
        toolbar.pack(fill="x", pady=(0, 5))
        
        self.result_info_label = ttk.Label(toolbar, text="No data")
        self.result_info_label.pack(side="left")
        
        # Pagination controls
        pagination_frame = ttk.Frame(toolbar)
        pagination_frame.pack(side="right")
        
        ttk.Button(pagination_frame, text="⏮️", command=self.first_page,
                  width=3).pack(side="left", padx=2)
        ttk.Button(pagination_frame, text="◀️", command=self.prev_page,
                  width=3).pack(side="left", padx=2)
        
        self.page_label = ttk.Label(pagination_frame, text="Page 1")
        self.page_label.pack(side="left", padx=10)
        
        ttk.Button(pagination_frame, text="▶️", command=self.next_page,
                  width=3).pack(side="left", padx=2)
        ttk.Button(pagination_frame, text="⏭️", command=self.last_page,
                  width=3).pack(side="left", padx=2)
        
        # Treeview
        tree_container = ttk.Frame(result_frame)
        tree_container.pack(fill="both", expand=True)
        
        tree_scroll_y = ttk.Scrollbar(tree_container)
        tree_scroll_y.pack(side="right", fill="y")
        
        tree_scroll_x = ttk.Scrollbar(tree_container, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")
        
        self.result_tree = ttk.Treeview(tree_container,
                                       yscrollcommand=tree_scroll_y.set,
                                       xscrollcommand=tree_scroll_x.set,
                                       style='Treeview')
        self.result_tree.pack(fill="both", expand=True)
        
        tree_scroll_y.config(command=self.result_tree.yview)
        tree_scroll_x.config(command=self.result_tree.xview)
        
        # Context menu
        self.tree_context_menu = tk.Menu(self.result_tree, tearoff=0,
                                        bg=ModernStyle.BG_SECONDARY,
                                        fg=ModernStyle.FG_PRIMARY)
        self.tree_context_menu.add_command(label="📋 Copy Cell", command=self.copy_cell)
        self.tree_context_menu.add_command(label="📄 Copy Row", command=self.copy_row)
        self.tree_context_menu.add_separator()
        self.tree_context_menu.add_command(label="🔍 Filter by Value", command=self.filter_by_value)
        
        self.result_tree.bind("<Button-3>", self.show_context_menu)
    
    def setup_sql_tab(self):
        """Thiết lập tab SQL Editor"""
        
        # Top toolbar
        toolbar = ttk.Frame(self.sql_tab)
        toolbar.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(toolbar, text="▶️ Execute",
                  command=self.execute_sql,
                  style='Success.TButton').pack(side="left", padx=5)
        ttk.Button(toolbar, text="🗑️ Clear",
                  command=self.clear_sql,
                  style='Danger.TButton').pack(side="left", padx=5)
        ttk.Button(toolbar, text="📁 Load SQL",
                  command=self.load_sql_file).pack(side="left", padx=5)
        ttk.Button(toolbar, text="💾 Save SQL",
                  command=self.save_sql_file).pack(side="left", padx=5)
        
        self.sql_info_label = ttk.Label(toolbar, text="Ready")
        self.sql_info_label.pack(side="right", padx=5)
        
        # SQL Editor
        editor_frame = ttk.LabelFrame(self.sql_tab, text="✏️ SQL Editor", padding=10)
        editor_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Line numbers and editor
        editor_container = ttk.Frame(editor_frame)
        editor_container.pack(fill="both", expand=True)
        
        self.sql_text = scrolledtext.ScrolledText(editor_container,
                                                  bg=ModernStyle.BG_SECONDARY,
                                                  fg=ModernStyle.FG_PRIMARY,
                                                  insertbackground=ModernStyle.FG_PRIMARY,
                                                  font=('Consolas', 10),
                                                  wrap=tk.NONE,
                                                  borderwidth=0,
                                                  highlightthickness=1,
                                                  highlightbackground=ModernStyle.BG_TERTIARY)
        self.sql_text.pack(fill="both", expand=True)
        
        # Sample queries
        self.sql_text.insert(1.0, """-- Sample Queries
-- SELECT * FROM table_name LIMIT 10;
-- SELECT column1, column2 FROM table_name WHERE column1 > 100;
-- SELECT * FROM table_name ORDER BY column1 DESC;

""")
        
        # Results
        result_frame = ttk.LabelFrame(self.sql_tab, text="📊 Query Results", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        result_container = ttk.Frame(result_frame)
        result_container.pack(fill="both", expand=True)
        
        sql_tree_scroll_y = ttk.Scrollbar(result_container)
        sql_tree_scroll_y.pack(side="right", fill="y")
        
        sql_tree_scroll_x = ttk.Scrollbar(result_container, orient="horizontal")
        sql_tree_scroll_x.pack(side="bottom", fill="x")
        
        self.sql_result_tree = ttk.Treeview(result_container,
                                           yscrollcommand=sql_tree_scroll_y.set,
                                           xscrollcommand=sql_tree_scroll_x.set,
                                           style='Treeview')
        self.sql_result_tree.pack(fill="both", expand=True)
        
        sql_tree_scroll_y.config(command=self.sql_result_tree.yview)
        sql_tree_scroll_x.config(command=self.sql_result_tree.xview)
    
    def setup_connection_tab(self):
        """Thiết lập tab Connection Manager"""
        
        # Connection form
        form_frame = ttk.LabelFrame(self.conn_tab, text="🔌 Connection Settings", padding=20)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        # Database Type
        row = 0
        ttk.Label(form_frame, text="Database Type:").grid(row=row, column=0, sticky="w", padx=5, pady=10)
        self.db_type_var = tk.StringVar(value='sqlite')
        db_combo = ttk.Combobox(form_frame, textvariable=self.db_type_var,
                               values=['sqlite', 'mysql', 'postgresql', 'mongodb'],
                               width=20, state='readonly')
        db_combo.grid(row=row, column=1, sticky="w", padx=5, pady=10)
        db_combo.bind('<<ComboboxSelected>>', self.on_db_type_change)
        
        # Host
        row += 1
        ttk.Label(form_frame, text="Host:").grid(row=row, column=0, sticky="w", padx=5, pady=10)
        self.host_var = tk.StringVar(value='localhost')
        ttk.Entry(form_frame, textvariable=self.host_var, width=30).grid(row=row, column=1, sticky="w", padx=5, pady=10)
        
        # Port
        ttk.Label(form_frame, text="Port:").grid(row=row, column=2, sticky="w", padx=5, pady=10)
        self.port_var = tk.StringVar(value='')
        ttk.Entry(form_frame, textvariable=self.port_var, width=10).grid(row=row, column=3, sticky="w", padx=5, pady=10)
        
        # User
        row += 1
        ttk.Label(form_frame, text="Username:").grid(row=row, column=0, sticky="w", padx=5, pady=10)
        self.user_var = tk.StringVar(value='root')
        ttk.Entry(form_frame, textvariable=self.user_var, width=30).grid(row=row, column=1, sticky="w", padx=5, pady=10)
        
        # Password
        ttk.Label(form_frame, text="Password:").grid(row=row, column=2, sticky="w", padx=5, pady=10)
        self.password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.password_var, show="*", width=20).grid(row=row, column=3, sticky="w", padx=5, pady=10)
        
        # Database/Path
        row += 1
        self.db_label = ttk.Label(form_frame, text="Database Path:")
        self.db_label.grid(row=row, column=0, sticky="w", padx=5, pady=10)
        self.database_var = tk.StringVar(value='database.db')
        self.db_entry = ttk.Entry(form_frame, textvariable=self.database_var, width=30)
        self.db_entry.grid(row=row, column=1, sticky="w", padx=5, pady=10)
        
        ttk.Button(form_frame, text="📁 Browse",
                  command=self.browse_db_file).grid(row=row, column=2, sticky="w", padx=5, pady=10)
        
        # Connection buttons
        row += 1
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=row, column=0, columnspan=4, pady=20)
        
        ttk.Button(btn_frame, text="🔌 Connect",
                  command=self.connect_db,
                  style='Success.TButton',
                  width=15).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="🔌 Disconnect",
                  command=self.disconnect_db,
                  style='Danger.TButton',
                  width=15).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="🧪 Test Connection",
                  command=self.test_connection,
                  width=15).pack(side="left", padx=10)
        
        # Connection info
        info_frame = ttk.LabelFrame(self.conn_tab, text="ℹ️ Connection Info", padding=20)
        info_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.conn_info_text = scrolledtext.ScrolledText(info_frame,
                                                        height=15,
                                                        bg=ModernStyle.BG_SECONDARY,
                                                        fg=ModernStyle.FG_PRIMARY,
                                                        font=('Consolas', 9),
                                                        borderwidth=0,
                                                        highlightthickness=1,
                                                        highlightbackground=ModernStyle.BG_TERTIARY)
        self.conn_info_text.pack(fill="both", expand=True)
        self.conn_info_text.insert(1.0, "No active connection\n")
        self.conn_info_text.config(state='disabled')
    
    def setup_status_bar(self, parent):
        """Thiết lập status bar"""
        status_frame = ttk.Frame(parent, style='Card.TFrame')
        status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="⚡ Ready")
        self.status_label.pack(side="left", padx=20, pady=10)
        
        self.time_label = ttk.Label(status_frame, text="")
        self.time_label.pack(side="right", padx=20, pady=10)
        
        self.update_time()
    
    def update_time(self):
        """Cập nhật thời gian"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"🕐 {current_time}")
        self.root.after(1000, self.update_time)
    
    # Connection methods
    def on_db_type_change(self, event=None):
        """Xử lý khi thay đổi loại database"""
        db_type = self.db_type_var.get()
        if db_type == 'sqlite':
            self.db_label.config(text="Database Path:")
            self.database_var.set('database.db')
            self.port_var.set('')
        elif db_type == 'mysql':
            self.db_label.config(text="Database Name:")
            self.database_var.set('test')
            self.port_var.set('3306')
        elif db_type == 'postgresql':
            self.db_label.config(text="Database Name:")
            self.database_var.set('postgres')
            self.port_var.set('5432')
        elif db_type == 'mongodb':
            self.db_label.config(text="Database Name:")
            self.database_var.set('test')
            self.port_var.set('27017')
    
    def browse_db_file(self):
        """Chọn file database"""
        filename = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("SQLite files", "*.db *.sqlite *.sqlite3"), ("All files", "*.*")]
        )
        if filename:
            self.database_var.set(filename)
    
    def test_connection(self):
        """Test kết nối"""
        self.status_label.config(text="🔄 Testing connection...")
        self.root.update()
        
        db_type = self.db_type_var.get()
        
        try:
            if db_type == 'sqlite':
                kwargs = {'path': self.database_var.get()}
            elif db_type == 'mongodb':
                kwargs = {
                    'uri': f"mongodb://{self.host_var.get()}:{self.port_var.get()}/",
                    'database': self.database_var.get()
                }
            else:
                kwargs = {
                    'host': self.host_var.get(),
                    'user': self.user_var.get(),
                    'password': self.password_var.get(),
                    'database': self.database_var.get(),
                    'port': int(self.port_var.get()) if self.port_var.get() else None
                }
            
            test_connector = DatabaseConnector(db_type, **kwargs)
            success, message = test_connector.connect()
            test_connector.close()
            
            if success:
                messagebox.showinfo("✅ Success", f"Connection test successful!\n\n{message}")
                self.status_label.config(text="✅ Test successful")
            else:
                messagebox.showerror("❌ Error", f"Connection test failed!\n\n{message}")
                self.status_label.config(text="❌ Test failed")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Connection test failed!\n\n{str(e)}")
            self.status_label.config(text="❌ Test failed")
    
    def connect_db(self):
        """Kết nối đến database"""
        self.status_label.config(text="🔄 Connecting...")
        self.root.update()
        
        try:
            db_type = self.db_type_var.get()
            
            if db_type == 'sqlite':
                kwargs = {'path': self.database_var.get()}
            elif db_type == 'mongodb':
                kwargs = {
                    'uri': f"mongodb://{self.host_var.get()}:{self.port_var.get()}/",
                    'database': self.database_var.get()
                }
            else:
                kwargs = {
                    'host': self.host_var.get(),
                    'user': self.user_var.get(),
                    'password': self.password_var.get(),
                    'database': self.database_var.get(),
                    'port': int(self.port_var.get()) if self.port_var.get() else None
                }
            
            self.connector = DatabaseConnector(db_type, **kwargs)
            success, message = self.connector.connect()
            
            if success:
                # Load tables
                tables = self.connector.get_tables()
                self.table_listbox.delete(0, tk.END)
                for table in tables:
                    self.table_listbox.insert(tk.END, table)
                
                # Update UI
                self.conn_status.config(text=f"🟢 Connected to {db_type}",
                                       foreground=ModernStyle.ACCENT_GREEN)
                self.status_label.config(text=f"✅ {message}")
                
                # Update connection info
                self.update_connection_info()
                
                messagebox.showinfo("✅ Success", f"{message}\n\nFound {len(tables)} tables")
            else:
                raise Exception(message)
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Connection failed!\n\n{str(e)}")
            self.status_label.config(text="❌ Connection failed")
            self.conn_status.config(text="⚫ Disconnected",
                                   foreground=ModernStyle.ACCENT_RED)
    
    def disconnect_db(self):
        """Ngắt kết nối"""
        if self.connector:
            self.connector.close()
            self.connector = None
            self.table_listbox.delete(0, tk.END)
            self.column_listbox.delete(0, tk.END)
            self.current_table = None
            
            self.conn_status.config(text="⚫ Disconnected",
                                   foreground=ModernStyle.ACCENT_RED)
            self.status_label.config(text="🔌 Disconnected")
            
            self.update_connection_info()
    
    def update_connection_info(self):
        """Cập nhật thông tin kết nối"""
        self.conn_info_text.config(state='normal')
        self.conn_info_text.delete(1.0, tk.END)
        
        if self.connector:
            info = f"""✅ Active Connection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Database Type: {self.connector.db_type.upper()}
Status: Connected
Connected at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Connection Details:
"""
            if self.connector.db_type == 'sqlite':
                info += f"  Path: {self.database_var.get()}\n"
            else:
                info += f"  Host: {self.host_var.get()}\n"
                info += f"  Port: {self.port_var.get()}\n"
                info += f"  Database: {self.database_var.get()}\n"
                info += f"  User: {self.user_var.get()}\n"
            
            try:
                tables = self.connector.get_tables()
                info += f"\nTables: {len(tables)}\n"
                info += f"\nAvailable Tables:\n"
                for table in tables:
                    try:
                        count = self.connector.get_row_count(table)
                        info += f"  • {table} ({count} rows)\n"
                    except:
                        info += f"  • {table}\n"
            except:
                pass
            
        else:
            info = "⚫ No active connection\n\nPlease configure and connect to a database."
        
        self.conn_info_text.insert(1.0, info)
        self.conn_info_text.config(state='disabled')
    
    # Table and column methods
    def filter_tables(self, *args):
        """Lọc bảng theo tên"""
        search_term = self.table_search_var.get().lower()
        if not self.connector:
            return
        
        try:
            all_tables = self.connector.get_tables()
            self.table_listbox.delete(0, tk.END)
            
            filtered_tables = [t for t in all_tables if search_term in t.lower()]
            for table in filtered_tables:
                self.table_listbox.insert(tk.END, table)
        except:
            pass
    
    def refresh_tables(self):
        """Refresh danh sách bảng"""
        if not self.connector:
            messagebox.showwarning("⚠️ Warning", "Please connect to a database first")
            return
        
        try:
            tables = self.connector.get_tables()
            self.table_listbox.delete(0, tk.END)
            for table in tables:
                self.table_listbox.insert(tk.END, table)
            
            self.status_label.config(text=f"✅ Refreshed {len(tables)} tables")
            self.update_connection_info()
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
    
    def on_table_select(self, event):
        """Xử lý khi chọn bảng"""
        selection = self.table_listbox.curselection()
        if not selection:
            return
        
        table_name = self.table_listbox.get(selection[0])
        self.current_table = table_name
        
        try:
            # Load columns
            columns = self.connector.get_columns(table_name)
            self.column_listbox.delete(0, tk.END)
            for col in columns:
                self.column_listbox.insert(tk.END, col)
            
            # Update filter combo
            self.filter_column_combo['values'] = columns
            
            # Get row count
            count = self.connector.get_row_count(table_name)
            self.status_label.config(text=f"📊 Table: {table_name} ({count} rows, {len(columns)} columns)")
            
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
    
    # Filter methods
    def add_filter(self):
        """Thêm filter"""
        col = self.filter_column_var.get()
        op = self.filter_op_var.get()
        val = self.filter_value_var.get()
        
        if not col or not val:
            messagebox.showwarning("⚠️ Warning", "Please fill in column and value")
            return
        
        # Convert data type
        try:
            if val.isdigit():
                val = int(val)
            elif val.replace('.', '', 1).replace('-', '', 1).isdigit():
                val = float(val)
        except:
            pass
        
        self.filters[col] = (op, val)
        self.update_filter_display()
        
        self.status_label.config(text=f"➕ Added filter: {col} {op} {val}")
    
    def update_filter_display(self):
        """Cập nhật hiển thị filter"""
        self.filter_text.config(state='normal')
        self.filter_text.delete(1.0, tk.END)
        
        if self.filters:
            for i, (col, (op, val)) in enumerate(self.filters.items(), 1):
                self.filter_text.insert(tk.END, f"{i}. {col} {op} {val}\n")
        else:
            self.filter_text.insert(tk.END, "No filters applied")
        
        self.filter_text.config(state='disabled')
    
    def clear_filters(self):
        """Xóa tất cả filter"""
        self.filters = {}
        self.update_filter_display()
        self.status_label.config(text="🗑️ All filters cleared")
    
    def filter_by_value(self):
        """Tạo filter từ giá trị đã chọn"""
        selection = self.result_tree.selection()
        if not selection:
            return
        
        item = self.result_tree.item(selection[0])
        values = item['values']
        
        # Get column index
        focused_column = self.result_tree.focus()
        if not focused_column:
            return
        
        # Ask user for column
        columns = self.result_tree['columns']
        # Use first column value for now
        if columns and values:
            col = columns[0]
            val = values[0]
            self.filter_column_var.set(col)
            self.filter_value_var.set(str(val))
            self.status_label.config(text=f"📋 Filter template created: {col} = {val}")
    
    # Sort methods
    def add_sort_asc(self):
        """Thêm cột sắp xếp tăng dần"""
        selection = self.column_listbox.curselection()
        if not selection:
            messagebox.showwarning("⚠️ Warning", "Please select a column")
            return
        
        for idx in selection:
            col = self.column_listbox.get(idx)
            self.sort_listbox.insert(tk.END, f"⬆️ {col}")
        
        self.status_label.config(text="⬆️ Added ascending sort")
    
    def add_sort_desc(self):
        """Thêm cột sắp xếp giảm dần"""
        selection = self.column_listbox.curselection()
        if not selection:
            messagebox.showwarning("⚠️ Warning", "Please select a column")
            return
        
        for idx in selection:
            col = self.column_listbox.get(idx)
            self.sort_listbox.insert(tk.END, f"⬇️ {col}")
        
        self.status_label.config(text="⬇️ Added descending sort")
    
    def remove_sort(self):
        """Xóa cột sắp xếp đã chọn"""
        selection = self.sort_listbox.curselection()
        if selection:
            self.sort_listbox.delete(selection[0])
            self.status_label.config(text="❌ Removed sort column")
    
    def clear_sorts(self):
        """Xóa tất cả sắp xếp"""
        self.sort_listbox.delete(0, tk.END)
        self.status_label.config(text="🗑️ All sorts cleared")
    
    def get_sort_config(self) -> Tuple[List[str], List[bool]]:
        """Lấy cấu hình sắp xếp"""
        sorts = list(self.sort_listbox.get(0, tk.END))
        columns = []
        ascending = []
        for s in sorts:
            if '⬆️' in s:
                columns.append(s.replace('⬆️ ', ''))
                ascending.append(True)
            else:
                columns.append(s.replace('⬇️ ', ''))
                ascending.append(False)
        return columns, ascending
    
    # Query and display methods
    def view_data(self):
        """Xem dữ liệu"""
        if not self.connector or not self.current_table:
            messagebox.showwarning("⚠️ Warning", "Please connect and select a table")
            return
        
        self.status_label.config(text="🔄 Querying data...")
        self.root.update()
        
        try:
            sort_cols, ascending = self.get_sort_config()
            
            limit_str = self.limit_var.get()
            limit = None if limit_str == 'All' else int(limit_str)
            
            self.pagination_limit = limit if limit else 1000
            self.pagination_offset = 0
            
            df = self.connector.query_data(
                self.current_table,
                filters=self.filters if self.filters else None,
                sort_columns=sort_cols if sort_cols else None,
                ascending=ascending if ascending else None,
                limit=self.pagination_limit,
                offset=self.pagination_offset
            )
            
            self.current_df = df
            self.display_dataframe(df, self.result_tree)
            
            total_rows = self.connector.get_row_count(self.current_table, self.filters if self.filters else None)
            self.result_info_label.config(text=f"📊 Showing {len(df)} of {total_rows} rows")
            self.status_label.config(text=f"✅ Query completed: {len(df)} rows")
            self.update_page_label()
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Query failed!\n\n{str(e)}")
            self.status_label.config(text="❌ Query failed")
    
    def display_dataframe(self, df, tree_widget):
        """Hiển thị DataFrame trong Treeview"""
        # Clear existing
        tree_widget.delete(*tree_widget.get_children())
        
        if df.empty:
            tree_widget['columns'] = []
            tree_widget['show'] = ''
            return
        
        # Setup columns
        tree_widget['columns'] = list(df.columns)
        tree_widget['show'] = 'headings'
        
        for col in df.columns:
            tree_widget.heading(col, text=col, command=lambda c=col: self.sort_by_column(c, tree_widget))
            tree_widget.column(col, width=120, minwidth=80)
        
        # Insert data
        for idx, row in df.iterrows():
            values = [str(val)[:100] if len(str(val)) > 100 else str(val) for val in row]
            tree_widget.insert('', tk.END, values=values)
    
    def sort_by_column(self, col, tree_widget):
        """Sắp xếp khi click vào header"""
        if self.current_df is not None:
            # Toggle sort direction
            if hasattr(self, 'last_sort_col') and self.last_sort_col == col:
                self.last_sort_asc = not self.last_sort_asc
            else:
                self.last_sort_col = col
                self.last_sort_asc = True
            
            sorted_df = self.current_df.sort_values(by=col, ascending=self.last_sort_asc)
            self.display_dataframe(sorted_df, tree_widget)
            
            direction = "↑" if self.last_sort_asc else "↓"
            self.status_label.config(text=f"🔽 Sorted by {col} {direction}")
    
    # Pagination methods
    def update_page_label(self):
        """Cập nhật label trang"""
        if self.pagination_limit:
            current_page = (self.pagination_offset // self.pagination_limit) + 1
            self.page_label.config(text=f"Page {current_page}")
        else:
            self.page_label.config(text="All")
    
    def first_page(self):
        """Trang đầu tiên"""
        self.pagination_offset = 0
        self.view_data()
    
    def prev_page(self):
        """Trang trước"""
        if self.pagination_offset >= self.pagination_limit:
            self.pagination_offset -= self.pagination_limit
            self.view_data()
    
    def next_page(self):
        """Trang tiếp theo"""
        self.pagination_offset += self.pagination_limit
        self.view_data()
    
    def last_page(self):
        """Trang cuối cùng"""
        if not self.connector or not self.current_table:
            return
        
        total_rows = self.connector.get_row_count(self.current_table, 
                                                  self.filters if self.filters else None)
        if self.pagination_limit:
            self.pagination_offset = (total_rows // self.pagination_limit) * self.pagination_limit
            self.view_data()
    
    # Context menu methods
    def show_context_menu(self, event):
        """Hiển thị context menu"""
        item = self.result_tree.identify_row(event.y)
        if item:
            self.result_tree.selection_set(item)
            self.tree_context_menu.post(event.x_root, event.y_root)
    
    def copy_cell(self):
        """Copy giá trị cell"""
        selection = self.result_tree.selection()
        if not selection:
            return
        
        # Get focused column
        column = self.result_tree.focus_get()
        item = self.result_tree.item(selection[0])
        values = item['values']
        
        if values:
            self.root.clipboard_clear()
            self.root.clipboard_append(str(values[0]))
            self.status_label.config(text="📋 Copied to clipboard")
    
    def copy_row(self):
        """Copy toàn bộ row"""
        selection = self.result_tree.selection()
        if not selection:
            return
        
        item = self.result_tree.item(selection[0])
        values = item['values']
        
        row_text = '\t'.join([str(v) for v in values])
        self.root.clipboard_clear()
        self.root.clipboard_append(row_text)
        self.status_label.config(text="📋 Row copied to clipboard")
    
    # SQL Editor methods
    def execute_sql(self):
        """Thực thi SQL query"""
        if not self.connector:
            messagebox.showwarning("⚠️ Warning", "Please connect to a database first")
            return
        
        if self.connector.db_type == 'mongodb':
            messagebox.showwarning("⚠️ Warning", "SQL Editor is not supported for MongoDB")
            return
        
        query = self.sql_text.get(1.0, tk.END).strip()
        if not query:
            messagebox.showwarning("⚠️ Warning", "Please enter a SQL query")
            return
        
        self.sql_info_label.config(text="🔄 Executing...")
        self.root.update()
        
        try:
            start_time = datetime.now()
            df = self.connector.execute_query(query)
            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()
            
            self.display_dataframe(df, self.sql_result_tree)
            
            self.sql_info_label.config(text=f"✅ Success: {len(df)} rows in {elapsed:.2f}s")
            self.status_label.config(text=f"✅ SQL executed: {len(df)} rows")
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"SQL execution failed!\n\n{str(e)}")
            self.sql_info_label.config(text="❌ Execution failed")
            self.status_label.config(text="❌ SQL execution failed")
    
    def clear_sql(self):
        """Xóa SQL editor"""
        self.sql_text.delete(1.0, tk.END)
        self.sql_result_tree.delete(*self.sql_result_tree.get_children())
        self.sql_info_label.config(text="Ready")
    
    def load_sql_file(self):
        """Load SQL từ file"""
        filename = filedialog.askopenfilename(
            title="Load SQL File",
            filetypes=[("SQL files", "*.sql"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.sql_text.delete(1.0, tk.END)
                self.sql_text.insert(1.0, content)
                self.status_label.config(text=f"📁 Loaded: {filename}")
            except Exception as e:
                messagebox.showerror("❌ Error", f"Failed to load file!\n\n{str(e)}")
    
    def save_sql_file(self):
        """Lưu SQL ra file"""
        filename = filedialog.asksaveasfilename(
            title="Save SQL File",
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                content = self.sql_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_label.config(text=f"💾 Saved: {filename}")
            except Exception as e:
                messagebox.showerror("❌ Error", f"Failed to save file!\n\n{str(e)}")
    
    # Export methods
    def export_csv(self):
        """Xuất ra CSV"""
        self._export_data('csv')
    
    def export_excel(self):
        """Xuất ra Excel"""
        self._export_data('excel')
    
    def export_json(self):
        """Xuất ra JSON"""
        self._export_data('json')
    
    def _export_data(self, format: str):
        """Xuất dữ liệu"""
        if not self.connector or not self.current_table:
            messagebox.showwarning("⚠️ Warning", "Please connect and select a table")
            return
        
        self.status_label.config(text=f"🔄 Exporting to {format.upper()}...")
        self.root.update()
        
        try:
            sort_cols, ascending = self.get_sort_config()
            
            # Get all data for export (no limit)
            df = self.connector.query_data(
                self.current_table,
                filters=self.filters if self.filters else None,
                sort_columns=sort_cols if sort_cols else None,
                ascending=ascending if ascending else None
            )
            
            if df.empty:
                messagebox.showwarning("⚠️ Warning", "No data to export")
                return
            
            # File dialog
            if format == 'csv':
                filename = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    initialfile=f"{self.current_table}_export.csv"
                )
                if filename:
                    df.to_csv(filename, index=False, encoding='utf-8-sig')
                    
            elif format == 'excel':
                filename = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    initialfile=f"{self.current_table}_export.xlsx"
                )
                if filename:
                    df.to_excel(filename, index=False, engine='openpyxl')
                    
            elif format == 'json':
                filename = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    initialfile=f"{self.current_table}_export.json"
                )
                if filename:
                    df.to_json(filename, orient='records', indent=2, force_ascii=False)
            
            if filename:
                messagebox.showinfo("✅ Success", 
                                  f"Exported {len(df)} rows to:\n{filename}")
                self.status_label.config(text=f"✅ Exported {len(df)} rows to {format.upper()}")
            else:
                self.status_label.config(text="❌ Export cancelled")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Export failed!\n\n{str(e)}")
            self.status_label.config(text="❌ Export failed")


def main():
    """Chạy ứng dụng"""
    root = tk.Tk()
    
    # Set icon if available
    try:
        root.iconbitmap('database.ico')
    except:
        pass
    
    app = DatabaseSortGUI(root)
    
    # Handle window close
    def on_closing():
        if app.connector:
            app.connector.close()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
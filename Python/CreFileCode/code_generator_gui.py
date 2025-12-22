#!/usr/bin/env python3
"""
Code File Generator GUI - Enhanced Version
A modern graphical user interface for the Code Generator Tool
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from code_generator import create_file, TEMPLATES, get_current_date


class CodeGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Code File Generator")
        self.root.geometry("750x650")
        self.root.minsize(650, 550)
        
        # Configure style with modern theme
        self.setup_styles()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Tab 1: Main generator
        self.main_tab = ttk.Frame(self.notebook, padding="25")
        self.notebook.add(self.main_tab, text="Generator")
        self.create_main_tab()
        
        # Tab 2: Settings & Info
        self.info_tab = ttk.Frame(self.notebook, padding="25")
        self.notebook.add(self.info_tab, text="Languages")
        self.create_info_tab()
        
    def setup_styles(self):
        """Configure custom styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define colors
        bg_color = "#f0f0f0"
        accent_color = "#0078d4"
        success_color = "#107c10"
        error_color = "#d83b01"
        
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground=accent_color)
        style.configure("Heading.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Normal.TLabel", font=("Segoe UI", 10))
        style.configure("Info.TLabel", font=("Segoe UI", 9), foreground="#666666")
        
        style.configure("TButton", font=("Segoe UI", 10))
        style.map("Success.TButton", 
                  background=[("active", success_color), ("pressed", "#0b6a0b")])
        
    def create_main_tab(self):
        """Create the main generator tab"""
        
        # Title
        title = ttk.Label(self.main_tab, text="📄 Create Code File", style="Title.TLabel")
        title.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        # Language selection with preview
        lang_frame = ttk.LabelFrame(self.main_tab, text="Language Selection", padding="15")
        lang_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(lang_frame, text="Select Language:", style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 8))
        
        self.language_var = tk.StringVar()
        languages = sorted(list(TEMPLATES.keys()))
        
        # Create language frame with grid
        lang_grid = ttk.Frame(lang_frame)
        lang_grid.pack(fill=tk.BOTH, expand=True)
        
        self.language_combo = ttk.Combobox(
            lang_grid,
            textvariable=self.language_var,
            values=languages,
            state="readonly",
            width=35,
            font=("Segoe UI", 10)
        )
        self.language_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.language_combo.current(0)
        
        self.language_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # Extension preview
        self.ext_label = ttk.Label(lang_grid, text="(.py)", style="Info.TLabel", width=8)
        self.ext_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Filename input
        filename_frame = ttk.LabelFrame(self.main_tab, text="File Details", padding="15")
        filename_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(filename_frame, text="Filename:", style="Heading.TLabel").grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        self.filename_var = tk.StringVar()
        self.filename_entry = ttk.Entry(filename_frame, textvariable=self.filename_var, font=("Segoe UI", 10))
        self.filename_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        self.filename_entry.bind("<KeyRelease>", self.on_filename_change)
        
        # Help text for filename
        help_text = ttk.Label(
            filename_frame, 
            text="✓ Spaces and special characters (except: < > : \" | ? *) are allowed", 
            style="Info.TLabel"
        )
        help_text.grid(row=0, column=2, padx=(10, 0), sticky=tk.W)
        
        # Full filename preview
        preview_frame = ttk.Frame(filename_frame)
        preview_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(preview_frame, text="Full Name:", style="Info.TLabel").pack(side=tk.LEFT)
        self.full_name_label = ttk.Label(preview_frame, text="example.py", style="Info.TLabel", foreground="#0078d4")
        self.full_name_label.pack(side=tk.LEFT, padx=(5, 0))
        
        filename_frame.columnconfigure(1, weight=1)
        
        # Output directory
        output_frame = ttk.LabelFrame(self.main_tab, text="Output Location", padding="15")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(output_frame, text="Directory:", style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 8))
        
        dir_input_frame = ttk.Frame(output_frame)
        dir_input_frame.pack(fill=tk.X)
        
        self.output_var = tk.StringVar(value=".")
        self.output_entry = ttk.Entry(dir_input_frame, textvariable=self.output_var, font=("Segoe UI", 10))
        self.output_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        browse_btn = ttk.Button(
            dir_input_frame,
            text="🗂️ Browse",
            command=self.browse_directory,
            width=12
        )
        browse_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Current path info
        current_path = ttk.Label(output_frame, text=f"Current: {os.getcwd()}", style="Info.TLabel")
        current_path.pack(anchor=tk.W, pady=(8, 0))
        
        # Action buttons
        button_frame = ttk.Frame(self.main_tab)
        button_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(25, 15))
        
        create_btn = ttk.Button(
            button_frame,
            text="✨ Create File",
            command=self.create_file_clicked,
            width=20
        )
        create_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = ttk.Button(
            button_frame,
            text="🔄 Reset",
            command=self.reset_form,
            width=15
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        open_btn = ttk.Button(
            button_frame,
            text="📂 Open Folder",
            command=self.open_folder,
            width=15
        )
        open_btn.pack(side=tk.LEFT, padx=5)
        
        # Output status
        status_frame = ttk.LabelFrame(self.main_tab, text="Status", padding="15")
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Status text with scrollbar
        text_frame = ttk.Frame(status_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = tk.Text(text_frame, height=8, wrap=tk.WORD, font=("Consolas", 9))
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text['yscrollcommand'] = scrollbar.set
        
        # Configure grid weights
        self.main_tab.columnconfigure(0, weight=1)
        self.main_tab.rowconfigure(5, weight=1)
        
        self.update_preview()
        
    def create_info_tab(self):
        """Create the languages information tab"""
        
        title = ttk.Label(self.info_tab, text="📚 Supported Languages", style="Title.TLabel")
        title.pack(pady=(0, 20), anchor=tk.W)
        
        # Create frame with scrollbar
        canvas_frame = ttk.Frame(self.info_tab)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add language info
        for lang, info in sorted(TEMPLATES.items()):
            lang_frame = ttk.LabelFrame(scrollable_frame, text=f"{lang.upper()}", padding="10")
            lang_frame.pack(fill=tk.X, pady=5, padx=5)
            
            info_text = f"Extension: {info['extension']}\nTemplate: {len(info['template'])} characters"
            ttk.Label(lang_frame, text=info_text, style="Info.TLabel", justify=tk.LEFT).pack(anchor=tk.W)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def on_language_change(self, event=None):
        """Handle language selection change"""
        self.update_preview()
        
    def on_filename_change(self, event=None):
        """Handle filename input change"""
        self.update_preview()
        
    def update_preview(self):
        """Update preview labels"""
        language = self.language_var.get()
        filename = self.filename_var.get().strip()
        
        if language:
            extension = TEMPLATES[language]['extension']
            self.ext_label.config(text=f"({extension})")
            
            if filename:
                full_name = filename if filename.endswith(extension) else filename + extension
            else:
                full_name = f"example{extension}"
            
            self.full_name_label.config(text=full_name)
    
    def is_valid_filename(self, filename):
        """
        Validate filename - allow spaces and special characters except Windows forbidden ones
        Forbidden: < > : " | ? *
        """
        forbidden_chars = ['<', '>', ':', '"', '|', '?', '*']
        
        for char in forbidden_chars:
            if char in filename:
                return False, f"Filename contains forbidden character: '{char}'"
        
        return True, "Valid"
    
    def browse_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_var.get()
        )
        if directory:
            self.output_var.set(directory)
    
    def open_folder(self):
        """Open the output directory in file explorer"""
        output_dir = self.output_var.get()
        
        if not os.path.exists(output_dir):
            messagebox.showwarning("Warning", f"Directory does not exist: {output_dir}")
            return
        
        os.startfile(os.path.abspath(output_dir))
    
    def create_file_clicked(self):
        """Handle create file button click"""
        language = self.language_var.get()
        filename = self.filename_var.get().strip()
        output_dir = self.output_var.get().strip()
        
        # Validation
        if not language:
            messagebox.showerror("Validation Error", "Please select a language")
            return
        
        if not filename:
            messagebox.showerror("Validation Error", "Please enter a filename")
            return
        
        # Validate filename for forbidden characters
        is_valid, msg = self.is_valid_filename(filename)
        if not is_valid:
            messagebox.showerror("Validation Error", f"Invalid filename!\n\n{msg}\n\nForbidden characters: < > : \" | ? *")
            return
        
        # Create file
        success, message = create_file(language, filename, output_dir)
        
        # Display result
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        
        if success:
            self.output_text.insert(tk.END, f"✅ {message}\n\nFile created successfully!")
            self.output_text.tag_add("success", "1.0", "1.2")
            messagebox.showinfo("Success", message)
            self.reset_form()
        else:
            self.output_text.insert(tk.END, f"❌ {message}")
            messagebox.showerror("Error", message)
    
    def reset_form(self):
        """Reset form to default values"""
        self.filename_var.set("")
        self.output_var.set(".")
        self.output_text.delete(1.0, tk.END)
        self.language_combo.current(0)
        self.update_preview()
        self.filename_entry.focus()


def main():
    root = tk.Tk()
    gui = CodeGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
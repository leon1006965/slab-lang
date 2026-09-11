#!/usr/bin/env python3
"""Slab IDE - A simple IDE for the Slab programming language."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess


class SlabIDE:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Slab IDE")
        self.root.geometry("1000x600")
        
        self.project_dir = None
        self.current_file = None
        self.files = {}
        
        self.setup_ui()
        self.new_project()
    
    def setup_ui(self):
        """Create the IDE interface."""
        # Toolbar
        self.toolbar = tk.Frame(self.root, bg="#2b2b2b", height=40)
        self.toolbar.pack(fill="x")
        
        # Run button
        self.run_btn = tk.Button(self.toolbar, text="▶ Run", 
                                  bg="#4CAF50", fg="white",
                                  command=self.run_project)
        self.run_btn.pack(side="left", padx=5, pady=5)
        
        # New Scene button
        self.new_scene_btn = tk.Button(self.toolbar, text="+ New Scene",
                                        command=self.new_scene)
        self.new_scene_btn.pack(side="left", padx=5, pady=5)
        
        # Project name
        self.project_label = tk.Label(self.toolbar, text="Project: Untitled",
                                       bg="#2b2b2b", fg="white")
        self.project_label.pack(side="left", padx=20)
        
        # Main container
        self.main_container = tk.PanedWindow(self.root, orient="horizontal")
        self.main_container.pack(fill="both", expand=True)
        
        # File panel (left)
        self.file_panel = tk.Frame(self.main_container, width=200, bg="#1e1e1e")
        self.main_container.add(self.file_panel)
        
        # File list
        self.file_label = tk.Label(self.file_panel, text="Files", 
                                    bg="#1e1e1e", fg="white")
        self.file_label.pack(pady=10)
        
        self.file_listbox = tk.Listbox(self.file_panel, bg="#252526", fg="white",
                                        selectbackground="#094771", relief="flat")
        self.file_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        
        # Editor panel (right)
        self.editor_panel = tk.Frame(self.main_container, bg="#1e1e1e")
        self.main_container.add(self.editor_panel)
        
        # Editor with line numbers
        self.editor_frame = tk.Frame(self.editor_panel, bg="#1e1e1e")
        self.editor_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Line numbers
        self.line_numbers = tk.Text(self.editor_frame, width=4, bg="#1e1e1e", 
                                     fg="#858585", relief="flat", state="disabled")
        self.line_numbers.pack(side="left", fill="y")
        
        # Code editor
        self.editor = tk.Text(self.editor_frame, bg="#1e1e1e", fg="#d4d4d4",
                               insertbackground="white", relief="flat",
                               undo=True, font=("Consolas", 12))
        self.editor.pack(side="right", fill="both", expand=True)
        
        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.editor)
        self.scrollbar.pack(side="right", fill="y")
        self.editor.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.editor.yview)
        
        # Bind editor events
        self.editor.bind("<KeyRelease>", self.update_line_numbers)
        self.editor.bind("<KeyRelease>", self.on_code_change)
        
        # Status bar
        self.status_bar = tk.Frame(self.root, bg="#007acc", height=25)
        self.status_bar.pack(fill="x")
        
        self.status_label = tk.Label(self.status_bar, text="Ready",
                                      bg="#007acc", fg="white")
        self.status_label.pack(side="left", padx=10)
        
        # Configure syntax highlighting tags
        self.editor.tag_configure("keyword", foreground="#569cd6")
        self.editor.tag_configure("tag", foreground="#4ec9b0")
        self.editor.tag_configure("attribute", foreground="#9cdcfe")
        self.editor.tag_configure("string", foreground="#ce9178")
    
    def new_project(self):
        """Create a new project."""
        # Ask for project location
        project_dir = filedialog.askdirectory(title="Select Project Folder")
        if not project_dir:
            project_dir = os.path.expanduser("~/slab_projects/untitled")
            os.makedirs(project_dir, exist_ok=True)
        
        self.project_dir = project_dir
        self.project_label.config(text=f"Project: {os.path.basename(project_dir)}")
        
        # Create Main.slab if it doesn't exist
        main_file = os.path.join(project_dir, "Main.slab")
        if not os.path.exists(main_file):
            with open(main_file, "w") as f:
                f.write('''<app>
  <window title="My App">
    <text big>Welcome to Slab!</text>
    <text>Edit Main.slab to get started</text>
    <button onclick="goto Scene1">Go to Scene 1</button>
  </window>
</app>
''')
        
        # Create Scene1.slab if it doesn't exist
        scene1_file = os.path.join(project_dir, "Scene1.slab")
        if not os.path.exists(scene1_file):
            with open(scene1_file, "w") as f:
                f.write('''<app>
  <window title="Scene 1">
    <text big>Scene 1</text>
    <text>This is the first scene</text>
    <button onclick="goto Main">Back to Main</button>
  </window>
</app>
''')
        
        self.refresh_file_list()
        self.open_file(main_file)
    
    def refresh_file_list(self):
        """Refresh the file list."""
        self.file_listbox.delete(0, tk.END)
        
        if not self.project_dir:
            return
        
        # Add Main.slab first
        main_file = os.path.join(self.project_dir, "Main.slab")
        if os.path.exists(main_file):
            self.file_listbox.insert(tk.END, "Main.slab")
        
        # Add other .slab files
        for f in sorted(os.listdir(self.project_dir)):
            if f.endswith(".slab") and f != "Main.slab":
                self.file_listbox.insert(tk.END, f)
    
    def on_file_select(self, event):
        """Handle file selection."""
        selection = self.file_listbox.curselection()
        if not selection:
            return
        
        filename = self.file_listbox.get(selection[0])
        filepath = os.path.join(self.project_dir, filename)
        self.open_file(filepath)
    
    def open_file(self, filepath):
        """Open a file in the editor."""
        if not os.path.exists(filepath):
            return
        
        # Save current file if needed
        if self.current_file:
            self.save_current_file()
        
        self.current_file = filepath
        
        # Read file content
        with open(filepath, "r") as f:
            content = f.read()
        
        # Update editor
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)
        
        # Update status
        filename = os.path.basename(filepath)
        self.status_label.config(text=f"Editing: {filename}")
        
        # Update line numbers
        self.update_line_numbers()
        
        # Apply syntax highlighting
        self.highlight_syntax()
    
    def save_current_file(self):
        """Save the current file."""
        if not self.current_file:
            return
        
        content = self.editor.get("1.0", tk.END)
        with open(self.current_file, "w") as f:
            f.write(content)
    
    def update_line_numbers(self, event=None):
        """Update line numbers."""
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        
        # Get number of lines
        content = self.editor.get("1.0", tk.END)
        num_lines = content.count("\n") + 1
        
        # Add line numbers
        for i in range(1, num_lines + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
        
        self.line_numbers.config(state="disabled")
    
    def on_code_change(self, event=None):
        """Handle code changes."""
        self.update_line_numbers()
        self.highlight_syntax()
        self.save_current_file()
    
    def highlight_syntax(self):
        """Apply basic syntax highlighting."""
        # Remove existing tags
        for tag in ["keyword", "tag", "attribute", "string"]:
            self.editor.tag_remove(tag, "1.0", tk.END)
        
        content = self.editor.get("1.0", tk.END)
        
        # Highlight tags (like <text>, <button>)
        import re
        for match in re.finditer(r"<(\w+)", content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add("tag", start, end)
        
        # Highlight attributes (like onclick=, title=)
        for match in re.finditer(r'(\w+)=', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add("attribute", start, end)
        
        # Highlight strings
        for match in re.finditer(r'"[^"]*"', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add("string", start, end)
    
    def run_project(self):
        """Run the current project."""
        if not self.project_dir:
            messagebox.showerror("Error", "No project open!")
            return
        
        self.save_current_file()
        
        main_file = os.path.join(self.project_dir, "Main.slab")
        if not os.path.exists(main_file):
            messagebox.showerror("Error", "Main.slab not found!")
            return
        
        try:
            # Run using slab
            slab_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            subprocess.Popen(
                ["python3", os.path.join(slab_dir, "slab.py"), "run", main_file],
                cwd=slab_dir
            )
            self.status_label.config(text="Running...")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run: {e}")
    
    def new_scene(self):
        """Create a new scene."""
        if not self.project_dir:
            messagebox.showerror("Error", "No project open!")
            return
        
        # Find next scene number
        scene_num = 1
        while os.path.exists(os.path.join(self.project_dir, f"Scene{scene_num}.slab")):
            scene_num += 1
        
        # Create scene file
        scene_file = os.path.join(self.project_dir, f"Scene{scene_num}.slab")
        with open(scene_file, "w") as f:
            f.write(f'''<app>
  <window title="Scene {scene_num}">
    <text big>Scene {scene_num}</text>
    <text>Edit this scene</text>
    <button onclick="goto Main">Back to Main</button>
  </window>
</app>
''')
        
        self.refresh_file_list()
        self.open_file(scene_file)
        self.status_label.config(text=f"Created Scene{scene_num}.slab")
    
    def run(self):
        """Start the IDE."""
        self.root.mainloop()


def main():
    ide = SlabIDE()
    ide.run()


if __name__ == "__main__":
    main()

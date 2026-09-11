#!/usr/bin/env python3
"""Slab IDE - A simple IDE for the Slab programming language."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import subprocess
import datetime


class DebugConsole:
    """Debug console that captures all output."""

    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="#1e1e1e")
        self.text = tk.Text(self.frame, bg="#0c0c0c", fg="#cccccc",
                            insertbackground="white", relief="flat",
                            font=("Consolas", 10), state="disabled",
                            wrap="word")
        self.text.pack(fill="both", expand=True)

        # Tags for colored output
        self.text.tag_configure("info", foreground="#4ec9b0")
        self.text.tag_configure("warn", foreground="#dcdcaa")
        self.text.tag_configure("error", foreground="#f44747")
        self.text.tag_configure("debug", foreground="#808080")
        self.text.tag_configure("success", foreground="#6a9955")

    def log(self, message, level="info"):
        """Write a message to the console."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        prefix = {"info": "[INFO]", "warn": "[WARN]", "error": "[ERR]",
                  "debug": "[DBG]", "success": "[OK]"}.get(level, "[?]")

        self.text.config(state="normal")
        self.text.insert("end", f"{timestamp} {prefix} {message}\n", level)
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")


class SlabIDE:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Slab IDE")
        self.root.geometry("1100x700")

        self.project_dir = None
        self.current_file = None

        self.setup_ui()
        self.debug("Slab IDE started")
        self.new_project()

    # ------------------------------------------------------------------ UI
    def setup_ui(self):
        """Create the IDE interface."""
        # Toolbar
        self.toolbar = tk.Frame(self.root, bg="#2b2b2b", height=40)
        self.toolbar.pack(fill="x")

        self.run_btn = tk.Button(self.toolbar, text="▶ Run",
                                 bg="#4CAF50", fg="white",
                                 command=self.run_project)
        self.run_btn.pack(side="left", padx=5, pady=5)

        self.new_scene_btn = tk.Button(self.toolbar, text="+ New Scene",
                                       command=self.new_scene)
        self.new_scene_btn.pack(side="left", padx=5, pady=5)

        self.build_btn = tk.Button(self.toolbar, text="🔨 Build",
                                   command=self.build_project)
        self.build_btn.pack(side="left", padx=5, pady=5)

        self.project_label = tk.Label(self.toolbar, text="Project: None",
                                      bg="#2b2b2b", fg="white")
        self.project_label.pack(side="left", padx=20)

        # Main area – vertical split: editor on top, debug on bottom
        self.main_pane = tk.PanedWindow(self.root, orient="vertical")
        self.main_pane.pack(fill="both", expand=True)

        # --- Top: file list + editor ---
        self.top_pane = tk.PanedWindow(self.main_pane, orient="horizontal")
        self.main_pane.add(self.top_pane)

        # File panel
        self.file_panel = tk.Frame(self.top_pane, width=180, bg="#1e1e1e")
        self.top_pane.add(self.file_panel)

        tk.Label(self.file_panel, text="Files", bg="#1e1e1e", fg="white"
                 ).pack(pady=5)

        self.file_listbox = tk.Listbox(self.file_panel, bg="#252526",
                                       fg="white",
                                       selectbackground="#094771",
                                       relief="flat")
        self.file_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)

        # Editor panel
        self.editor_panel = tk.Frame(self.top_pane, bg="#1e1e1e")
        self.top_pane.add(self.editor_panel)

        self.editor_frame = tk.Frame(self.editor_panel, bg="#1e1e1e")
        self.editor_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.line_numbers = tk.Text(self.editor_frame, width=4,
                                    bg="#1e1e1e", fg="#858585",
                                    relief="flat", state="disabled")
        self.line_numbers.pack(side="left", fill="y")

        self.editor = tk.Text(self.editor_frame, bg="#1e1e1e", fg="#d4d4d4",
                              insertbackground="white", relief="flat",
                              undo=True, font=("Consolas", 12))
        self.editor.pack(side="right", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.editor)
        self.scrollbar.pack(side="right", fill="y")
        self.editor.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.editor.yview)

        self.editor.bind("<KeyRelease>", self.on_code_change)

        # --- Bottom: debug console ---
        self.debug_console = DebugConsole(self.main_pane)
        self.main_pane.add(self.debug_console.frame)

        # Status bar
        self.status_bar = tk.Frame(self.root, bg="#007acc", height=25)
        self.status_bar.pack(fill="x", side="bottom")

        self.status_label = tk.Label(self.status_bar, text="Ready",
                                     bg="#007acc", fg="white")
        self.status_label.pack(side="left", padx=10)

        # Syntax highlighting tags
        self.editor.tag_configure("tag", foreground="#4ec9b0")
        self.editor.tag_configure("attribute", foreground="#9cdcfe")
        self.editor.tag_configure("string", foreground="#ce9178")

    # ------------------------------------------------------------- logging
    def debug(self, msg):
        self.debug_console.log(msg, "debug")

    def info(self, msg):
        self.debug_console.log(msg, "info")

    def warn(self, msg):
        self.debug_console.log(msg, "warn")

    def error(self, msg):
        self.debug_console.log(msg, "error")

    def ok(self, msg):
        self.debug_console.log(msg, "success")

    # ----------------------------------------------------------- file mgmt
    def new_project(self):
        project_dir = filedialog.askdirectory(title="Select Project Folder")
        if not project_dir:
            project_dir = os.path.expanduser("~/slab_projects/untitled")
            os.makedirs(project_dir, exist_ok=True)

        self.project_dir = project_dir
        self.project_label.config(text=f"Project: {os.path.basename(project_dir)}")
        self.info(f"Opened project: {project_dir}")

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
            self.debug("Created Main.slab")

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
            self.debug("Created Scene1.slab")

        self.refresh_file_list()
        self.open_file(main_file)

    def refresh_file_list(self):
        self.file_listbox.delete(0, tk.END)
        if not self.project_dir:
            return

        main_file = os.path.join(self.project_dir, "Main.slab")
        if os.path.exists(main_file):
            self.file_listbox.insert(tk.END, "Main.slab")

        for f in sorted(os.listdir(self.project_dir)):
            if f.endswith(".slab") and f != "Main.slab":
                self.file_listbox.insert(tk.END, f)

        count = self.file_listbox.size()
        self.debug(f"File list refreshed: {count} file(s)")

    def on_file_select(self, event):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        filename = self.file_listbox.get(selection[0])
        filepath = os.path.join(self.project_dir, filename)
        self.open_file(filepath)

    def open_file(self, filepath):
        if not os.path.exists(filepath):
            self.error(f"File not found: {filepath}")
            return

        if self.current_file:
            self.save_current_file()

        self.current_file = filepath
        with open(filepath, "r") as f:
            content = f.read()

        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)

        filename = os.path.basename(filepath)
        self.status_label.config(text=f"Editing: {filename}")
        self.info(f"Opened: {filename}")

        self.update_line_numbers()
        self.highlight_syntax()

    def save_current_file(self):
        if not self.current_file:
            return
        content = self.editor.get("1.0", tk.END)
        with open(self.current_file, "w") as f:
            f.write(content)
        self.debug(f"Saved: {os.path.basename(self.current_file)}")

    # -------------------------------------------------------- editor utils
    def update_line_numbers(self, event=None):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        content = self.editor.get("1.0", tk.END)
        num_lines = content.count("\n") + 1
        for i in range(1, num_lines + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
        self.line_numbers.config(state="disabled")

    def on_code_change(self, event=None):
        self.update_line_numbers()
        self.highlight_syntax()
        self.save_current_file()

    def highlight_syntax(self):
        for tag in ["tag", "attribute", "string"]:
            self.editor.tag_remove(tag, "1.0", tk.END)

        import re
        content = self.editor.get("1.0", tk.END)

        for match in re.finditer(r"<(/?)(\w+)", content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add("tag", start, end)

        for match in re.finditer(r'(\w+)=', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add("attribute", start, end)

        for match in re.finditer(r'"[^"]*"', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add("string", start, end)

    # ----------------------------------------------------------- build/run
    def run_project(self):
        if not self.project_dir:
            self.error("No project open!")
            return

        self.save_current_file()
        main_file = os.path.join(self.project_dir, "Main.slab")
        if not os.path.exists(main_file):
            self.error("Main.slab not found!")
            return

        self.info(f"Running {os.path.basename(self.project_dir)}...")

        try:
            slab_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            proc = subprocess.Popen(
                [sys.executable, os.path.join(slab_dir, "slab.py"),
                 "run", main_file],
                cwd=slab_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Read output in background
            def read_output():
                for line in proc.stdout:
                    self.info(line.strip())
                for line in proc.stderr:
                    self.error(line.strip())
                proc.wait()
                if proc.returncode == 0:
                    self.ok("Process finished (exit 0)")
                else:
                    self.error(f"Process failed (exit {proc.returncode})")

            import threading
            threading.Thread(target=read_output, daemon=True).start()
            self.ok("App launched")

        except Exception as e:
            self.error(f"Failed to run: {e}")

    def build_project(self):
        if not self.project_dir:
            self.error("No project open!")
            return

        self.save_current_file()
        self.info("Building project...")

        try:
            slab_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            result = subprocess.run(
                [sys.executable, os.path.join(slab_dir, "slab.py"),
                 "build-all", self.project_dir],
                cwd=slab_dir,
                capture_output=True,
                text=True
            )
            if result.stdout:
                self.ok(result.stdout.strip())
            if result.stderr:
                self.error(result.stderr.strip())
        except Exception as e:
            self.error(f"Build failed: {e}")

    def new_scene(self):
        if not self.project_dir:
            self.error("No project open!")
            return

        scene_num = 1
        while os.path.exists(os.path.join(self.project_dir,
                                          f"Scene{scene_num}.slab")):
            scene_num += 1

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
        self.ok(f"Created Scene{scene_num}.slab")

    def run(self):
        self.root.mainloop()


def main():
    ide = SlabIDE()
    ide.run()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Slab IDE - A reliable IDE for the Slab programming language."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import sys
import datetime
import traceback

# Make sure we can import slab modules
SLAB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SLAB_DIR)

from parser import parse_slab
from compiler import compile_to_python, compile_project, load_addons


class DebugConsole:
    """Debug console that captures all output."""

    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="#1e1e1e")

        header = tk.Frame(self.frame, bg="#252526")
        header.pack(fill="x")
        tk.Label(header, text="Console", bg="#252526", fg="white",
                 font=("Consolas", 10)).pack(side="left", padx=5)
        tk.Button(header, text="Clear", command=self.clear,
                  bg="#3c3c3c", fg="white", relief="flat").pack(side="right", padx=5)

        self.text = scrolledtext.ScrolledText(self.frame, bg="#0c0c0c",
                                              fg="#cccccc",
                                              font=("Consolas", 10),
                                              state="disabled",
                                              wrap="word", height=8)
        self.text.pack(fill="both", expand=True)

        self.text.tag_configure("info", foreground="#4ec9b0")
        self.text.tag_configure("warn", foreground="#dcdcaa")
        self.text.tag_configure("error", foreground="#f44747")
        self.text.tag_configure("success", foreground="#6a9955")

    def log(self, message, level="info"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        prefix = {"info": "[INFO]", "warn": "[WARN]", "error": "[ERR]",
                  "success": "[OK]"}.get(level, "[?]")
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
        self.root.geometry("1100x750")
        self.root.minsize(800, 500)

        self.project_dir = None
        self.current_file = None
        self.modified = False

        self.setup_ui()
        self.log("Slab IDE ready", "success")
        self.new_project()

    # ---------------------------------------------------------------- UI
    def setup_ui(self):
        # --- Menu bar ---
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_current_file)
        file_menu.add_command(label="Save All", command=self.save_all)
        menubar.add_cascade(label="File", menu=file_menu)

        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="Run Project", command=self.run_project)
        run_menu.add_command(label="Build Project", command=self.build_project)
        menubar.add_cascade(label="Run", menu=run_menu)

        scene_menu = tk.Menu(menubar, tearoff=0)
        scene_menu.add_command(label="New Scene", command=self.new_scene)
        menubar.add_cascade(label="Scene", menu=scene_menu)

        self.root.config(menu=menubar)

        # --- Toolbar ---
        toolbar = tk.Frame(self.root, bg="#2b2b2b", height=36)
        toolbar.pack(fill="x")

        tk.Button(toolbar, text="▶ Run", bg="#4CAF50", fg="white",
                  relief="flat", command=self.run_project
                  ).pack(side="left", padx=4, pady=4)
        tk.Button(toolbar, text="+ Scene", bg="#2196F3", fg="white",
                  relief="flat", command=self.new_scene
                  ).pack(side="left", padx=4, pady=4)
        tk.Button(toolbar, text="🔨 Build", bg="#FF9800", fg="white",
                  relief="flat", command=self.build_project
                  ).pack(side="left", padx=4, pady=4)

        self.project_label = tk.Label(toolbar, text="No project",
                                      bg="#2b2b2b", fg="white")
        self.project_label.pack(side="left", padx=15)

        # --- Main area ---
        main_pane = tk.PanedWindow(self.root, orient="vertical")
        main_pane.pack(fill="both", expand=True)

        # Top: file list + editor
        top_pane = tk.PanedWindow(main_pane, orient="horizontal")
        main_pane.add(top_pane)

        # File panel
        file_panel = tk.Frame(top_pane, width=180, bg="#1e1e1e")
        top_pane.add(file_panel)

        tk.Label(file_panel, text="Files", bg="#1e1e1e", fg="white",
                 font=("Consolas", 10, "bold")).pack(pady=6)

        self.file_listbox = tk.Listbox(file_panel, bg="#252526", fg="white",
                                       selectbackground="#094771",
                                       relief="flat", font=("Consolas", 11))
        self.file_listbox.pack(fill="both", expand=True, padx=4, pady=4)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        self.file_listbox.bind("<Button-3>", self.on_file_right_click)

        # Editor
        editor_panel = tk.Frame(top_pane, bg="#1e1e1e")
        top_pane.add(editor_panel)

        editor_frame = tk.Frame(editor_panel, bg="#1e1e1e")
        editor_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self.line_numbers = tk.Text(editor_frame, width=4, bg="#1e1e1e",
                                    fg="#858585", relief="flat",
                                    state="disabled", font=("Consolas", 12))
        self.line_numbers.pack(side="left", fill="y")

        self.editor = tk.Text(editor_frame, bg="#1e1e1e", fg="#d4d4d4",
                              insertbackground="white", relief="flat",
                              undo=True, font=("Consolas", 12),
                              tabs=4)
        self.editor.pack(side="right", fill="both", expand=True)

        scroll = tk.Scrollbar(self.editor, command=self.editor.yview)
        scroll.pack(side="right", fill="y")
        self.editor.config(yscrollcommand=scroll.set)

        self.editor.bind("<KeyRelease>", self.on_code_change)
        self.editor.bind("<Control-s>", lambda e: self.save_current_file())

        # Syntax highlighting
        self.editor.tag_configure("tag", foreground="#4ec9b0")
        self.editor.tag_configure("attr", foreground="#9cdcfe")
        self.editor.tag_configure("string", foreground="#ce9178")
        self.editor.tag_configure("comment", foreground="#6a9955")

        # Bottom: debug console
        self.debug_console = DebugConsole(main_pane)
        main_pane.add(self.debug_console.frame)

        # Status bar
        self.status_bar = tk.Frame(self.root, bg="#007acc", height=22)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_label = tk.Label(self.status_bar, text="Ready",
                                     bg="#007acc", fg="white",
                                     font=("Consolas", 9))
        self.status_label.pack(side="left", padx=8)

    # ----------------------------------------------------------- logging
    def log(self, msg, level="info"):
        try:
            self.debug_console.log(msg, level)
        except Exception:
            pass  # Widget already destroyed (app closed)

    # --------------------------------------------------------- file ops
    def new_project(self):
        d = filedialog.askdirectory(title="Select or create project folder")
        if not d:
            d = os.path.expanduser("~/slab_projects/myapp")
            os.makedirs(d, exist_ok=True)
        self._init_project(d)

    def open_project(self):
        d = filedialog.askdirectory(title="Open project folder")
        if d:
            self._init_project(d)

    def _init_project(self, d):
        self.project_dir = d
        self.project_label.config(text=f"Project: {os.path.basename(d)}")
        self.log(f"Project: {d}")

        main = os.path.join(d, "Main.slab")
        if not os.path.exists(main):
            with open(main, "w") as f:
                f.write('<app>\n  <window title="My App">\n'
                        '    <text big>Welcome to Slab!</text>\n'
                        '    <button onclick="goto Scene1">Scene 1</button>\n'
                        '  </window>\n</app>\n')
            self.log("Created Main.slab")

        s1 = os.path.join(d, "Scene1.slab")
        if not os.path.exists(s1):
            with open(s1, "w") as f:
                f.write('<app>\n  <window title="Scene 1">\n'
                        '    <text big>Scene 1</text>\n'
                        '    <button onclick="goto Main">Back</button>\n'
                        '  </window>\n</app>\n')
            self.log("Created Scene1.slab")

        self.refresh_files()
        self.open_file(main)

    def refresh_files(self):
        self.file_listbox.delete(0, tk.END)
        if not self.project_dir:
            return
        main = os.path.join(self.project_dir, "Main.slab")
        if os.path.exists(main):
            self.file_listbox.insert(tk.END, "Main.slab")
        for f in sorted(os.listdir(self.project_dir)):
            if f.endswith(".slab") and f != "Main.slab":
                self.file_listbox.insert(tk.END, f)

    def on_file_select(self, event):
        sel = self.file_listbox.curselection()
        if not sel:
            return
        name = self.file_listbox.get(sel[0])
        self.open_file(os.path.join(self.project_dir, name))

    def on_file_right_click(self, event):
        """Right-click context menu for files."""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Rename", command=self.rename_scene)
        menu.add_command(label="Delete", command=self.delete_scene)
        menu.post(event.x_root, event.y_root)

    def open_file(self, path):
        if not os.path.exists(path):
            self.log(f"Not found: {path}", "error")
            return
        if self.current_file and self.modified:
            self.save_current_file()

        self.current_file = path
        with open(path, "r") as f:
            content = f.read()

        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)
        self.modified = False

        name = os.path.basename(path)
        self.status_label.config(text=f"Editing: {name}")
        self.log(f"Opened {name}")
        self.update_line_numbers()
        self.highlight_syntax()

    def save_current_file(self):
        if not self.current_file:
            return
        content = self.editor.get("1.0", tk.END)
        with open(self.current_file, "w") as f:
            f.write(content)
        self.modified = False
        self.log(f"Saved {os.path.basename(self.current_file)}")

    def save_all(self):
        if self.current_file:
            self.save_current_file()

    # -------------------------------------------------------- editor
    def update_line_numbers(self, event=None):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        n = self.editor.get("1.0", tk.END).count("\n") + 1
        self.line_numbers.insert("1.0", "\n".join(str(i) for i in range(1, n + 1)))
        self.line_numbers.config(state="disabled")

    def on_code_change(self, event=None):
        self.modified = True
        self.update_line_numbers()
        self.highlight_syntax()

    def highlight_syntax(self):
        for t in ("tag", "attr", "string", "comment"):
            self.editor.tag_remove(t, "1.0", tk.END)
        import re
        c = self.editor.get("1.0", tk.END)
        for m in re.finditer(r"<\/?\w+", c):
            self.editor.tag_add("tag", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        for m in re.finditer(r'\w+(?==)', c):
            self.editor.tag_add("attr", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        for m in re.finditer(r'"[^"]*"', c):
            self.editor.tag_add("string", f"1.0+{m.start()}c", f"1.0+{m.end()}c")

    # --------------------------------------------------- run / build
    def _get_slab_dir(self):
        return SLAB_DIR

    def run_project(self):
        if not self.project_dir:
            self.log("No project open!", "error")
            return

        self.save_current_file()
        self.log("Running project...")

        try:
            # Load addons and compile
            load_addons(self.project_dir)
            python_code = compile_project(self.project_dir)

            # Write compiled code to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py',
                                             delete=False, dir='/tmp') as f:
                f.write(python_code)
                tmp_file = f.name

            self.log(f"Compiled to {tmp_file}")

            # Run as subprocess so it doesn't kill the IDE
            import subprocess
            proc = subprocess.Popen(
                [sys.executable, tmp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Read output in background thread
            def read_output():
                try:
                    for line in proc.stdout:
                        self.log(line.strip())
                    for line in proc.stderr:
                        self.log(line.strip(), "error")
                    proc.wait()
                    self.log(f"Process exited (code {proc.returncode})",
                             "success" if proc.returncode == 0 else "error")
                except Exception:
                    pass

            import threading
            t = threading.Thread(target=read_output, daemon=True)
            t.start()

        except Exception as e:
            tb = traceback.format_exc()
            for line in tb.strip().split("\n"):
                self.log(line, "error")

    def build_project(self):
        if not self.project_dir:
            self.log("No project open!", "error")
            return

        self.save_current_file()
        self.log("Building...")

        try:
            load_addons(self.project_dir)
            python_code = compile_project(self.project_dir)
            out = os.path.join(self.project_dir, "project.py")
            with open(out, "w") as f:
                f.write(python_code)
            self.log(f"Built: {out}", "success")
        except Exception as e:
            tb = traceback.format_exc()
            for line in tb.strip().split("\n"):
                self.log(line, "error")

    # --------------------------------------------------- scenes
    def new_scene(self):
        if not self.project_dir:
            self.log("No project open!", "error")
            return

        num = 1
        while os.path.exists(os.path.join(self.project_dir, f"Scene{num}.slab")):
            num += 1

        path = os.path.join(self.project_dir, f"Scene{num}.slab")
        with open(path, "w") as f:
            f.write(f'<app>\n  <window title="Scene {num}">\n'
                    f'    <text big>Scene {num}</text>\n'
                    f'    <button onclick="goto Main">Back</button>\n'
                    f'  </window>\n</app>\n')

        self.refresh_files()
        self.open_file(path)
        self.log(f"Created Scene{num}.slab", "success")

    def rename_scene(self):
        sel = self.file_listbox.curselection()
        if not sel:
            return
        old_name = self.file_listbox.get(sel[0])
        old_path = os.path.join(self.project_dir, old_name)

        dialog = tk.Toplevel(self.root)
        dialog.title("Rename Scene")
        dialog.geometry("300x100")
        tk.Label(dialog, text="New name:").pack(pady=5)
        entry = tk.Entry(dialog)
        entry.insert(0, old_name.replace(".slab", ""))
        entry.pack(pady=5)

        def do_rename():
            new = entry.get().strip() + ".slab"
            new_path = os.path.join(self.project_dir, new)
            os.rename(old_path, new_path)
            if self.current_file == old_path:
                self.current_file = new_path
            self.refresh_files()
            dialog.destroy()
            self.log(f"Renamed {old_name} -> {new}", "success")

        tk.Button(dialog, text="Rename", command=do_rename).pack(pady=5)

    def delete_scene(self):
        sel = self.file_listbox.curselection()
        if not sel:
            return
        name = self.file_listbox.get(sel[0])
        if name == "Main.slab":
            self.log("Cannot delete Main.slab", "error")
            return

        if messagebox.askyesno("Delete", f"Delete {name}?"):
            path = os.path.join(self.project_dir, name)
            os.remove(path)
            if self.current_file == path:
                self.current_file = None
            self.refresh_files()
            self.log(f"Deleted {name}")

    # --------------------------------------------------- main
    def run(self):
        self.root.mainloop()


def main():
    ide = SlabIDE()
    ide.run()


if __name__ == "__main__":
    main()

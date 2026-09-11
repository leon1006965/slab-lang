#!/usr/bin/env python3
"""Slab - A simple programming language like HTML."""

import sys
import os
import subprocess
from parser import parse_slab
from compiler import compile_to_python, compile_project, load_addons


def run_slab(filename: str):
    """Run a .slab file or project."""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        return
    
    # Check if this is a project directory with Main.slab
    project_dir = os.path.dirname(os.path.abspath(filename))
    main_file = os.path.join(project_dir, "Main.slab")
    
    if os.path.exists(main_file):
        # Run as project - compile all scenes into one file
        load_addons(project_dir)
        python_code = compile_project(project_dir)
    else:
        # Run single file
        with open(filename, 'r') as f:
            code = f.read()
        tree = parse_slab(code)
        python_code = compile_to_python(tree)
    
    # Write to temp file and run
    temp_file = "/tmp/slab_temp.py"
    with open(temp_file, 'w') as f:
        f.write(python_code)
    
    print(f"Running {filename}...")
    subprocess.run([sys.executable, temp_file])


def build_slab(filename: str):
    """Build a .slab file to Python."""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        return
    
    with open(filename, 'r') as f:
        code = f.read()
    
    tree = parse_slab(code)
    python_code = compile_to_python(tree)
    
    output = filename.replace('.slab', '.py')
    with open(output, 'w') as f:
        f.write(python_code)
    
    print(f"Built {output}")


def build_project(project_dir: str):
    """Build all .slab files in a project."""
    if not os.path.exists(project_dir):
        print(f"Error: Directory '{project_dir}' not found")
        return
    
    python_code = compile_project(project_dir)
    
    output = os.path.join(project_dir, "project.py")
    with open(output, 'w') as f:
        f.write(python_code)
    
    print(f"Built {output}")


def new_slab(name: str):
    """Create a new Slab project."""
    os.makedirs(name, exist_ok=True)
    
    main_template = f'''<app>
  <window title="{name}">
    <text big>Welcome to {name}!</text>
    <text>Edit Main.slab to get started</text>
    <button onclick="goto Scene1">Go to Scene 1</button>
  </window>
</app>
'''
    
    scene1_template = '''<app>
  <window title="Scene 1">
    <text big>Scene 1</text>
    <text>This is the first scene</text>
    <button onclick="goto Main">Back to Main</button>
  </window>
</app>
'''
    
    with open(os.path.join(name, "Main.slab"), "w") as f:
        f.write(main_template)
    
    with open(os.path.join(name, "Scene1.slab"), "w") as f:
        f.write(scene1_template)
    
    print(f"Created project: {name}")
    print(f"Run with: slab run {name}/Main.slab")


def ide():
    """Launch the Slab IDE."""
    ide_path = os.path.join(os.path.dirname(__file__), "ide", "ide.py")
    subprocess.run([sys.executable, ide_path])


def main():
    if len(sys.argv) < 2:
        print("Slab - A simple programming language")
        print("")
        print("Usage:")
        print("  slab run <file.slab>     Run a Slab file")
        print("  slab build <file.slab>   Build to Python")
        print("  slab build-all <dir>     Build project")
        print("  slab new <name>          Create new project")
        print("  slab ide                 Launch the IDE")
        return
    
    command = sys.argv[1]
    
    if command == "run" and len(sys.argv) >= 3:
        run_slab(sys.argv[2])
    elif command == "build" and len(sys.argv) >= 3:
        build_slab(sys.argv[2])
    elif command == "build-all" and len(sys.argv) >= 3:
        build_project(sys.argv[2])
    elif command == "new" and len(sys.argv) >= 3:
        new_slab(sys.argv[2])
    elif command == "ide":
        ide()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()

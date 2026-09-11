import os
import re
import json
import sys
from parser import Node, get_text, find_children, parse_slab


# Addon storage
addons = {}


def load_addons(project_dir: str):
    """Load addons from the project's addons folder."""
    global addons
    addons = {}

    addons_dir = os.path.join(project_dir, 'addons')
    if not os.path.exists(addons_dir):
        return

    for addon_name in os.listdir(addons_dir):
        addon_path = os.path.join(addons_dir, addon_name)
        if not os.path.isdir(addon_path):
            continue

        for filename in os.listdir(addon_path):
            if filename.endswith('.json'):
                json_path = os.path.join(addon_path, filename)
                try:
                    with open(json_path, 'r') as f:
                        config = json.load(f)

                    py_file = config.get('python', filename.replace('.json', '.py'))
                    py_path = os.path.join(addon_path, py_file)

                    if os.path.exists(py_path):
                        with open(py_path, 'r') as f:
                            py_code = f.read()

                        addons[config['tag']] = {
                            'config': config,
                            'code': py_code
                        }
                        print(f"[Slab] Loaded addon: {config['tag']}")
                except Exception as e:
                    print(f"[Slab] Error loading addon {addon_name}: {e}")


def compile_project(project_dir: str) -> str:
    """Compile all .slab files into a single Python app."""
    load_addons(project_dir)

    python_code = [
        "import tkinter as tk",
        "from tkinter import messagebox",
        "import os",
        "import sys",
        "",
        "# Scene storage",
        "scenes = {}",
        "current_window = None",
        "",
        "# Text elements storage (for <change> action)",
        "texts = {}",
        "",
        "# Variables storage (for <setvar> action)",
        "vars = {}",
        "",
        "# Addon functions storage",
        "addon_funcs = {}",
        "",
    ]

    # Add addon code with unique function names
    if addons:
        python_code.append("# Addon code")
        for tag, addon in addons.items():
            code = addon['code'].replace('def run(', f'def run_{tag}(')
            python_code.append(f"# Addon: {tag}")
            python_code.append(code)
            python_code.append(f"addon_funcs['{tag}'] = run_{tag}")
            python_code.append("")
        python_code.append("")

    # Load all .slab files
    slab_files = {}
    for filename in sorted(os.listdir(project_dir)):
        if filename.endswith('.slab'):
            scene_name = filename.replace('.slab', '')
            filepath = os.path.join(project_dir, filename)
            with open(filepath, 'r') as f:
                slab_files[scene_name] = f.read()

    # Pass 1: Extract ALL <function> blocks from all scenes
    all_functions = []
    for scene_name, code in slab_files.items():
        tree = parse_slab(code)
        # Top-level <function> blocks
        for child in tree.children:
            if child.tag == "function":
                all_functions.append(compile_function(child))
        # <function> blocks inside <app>
        for child in tree.children:
            if child.tag == "app":
                for sub in child.children:
                    if sub.tag == "function":
                        all_functions.append(compile_function(sub))
                    elif sub.tag == "window":
                        for elem in sub.children:
                            if elem.tag == "function":
                                all_functions.append(compile_function(elem))

    for func in all_functions:
        python_code.append("")
        python_code.extend(func)

    # Pass 2: Compile each scene (widgets only, no functions)
    for scene_name, code in slab_files.items():
        tree = parse_slab(code)
        scene_code = compile_scene(scene_name, tree)
        python_code.extend(scene_code)
        python_code.append("")
        python_code.append("")

    # Add goto function
    python_code.extend(compile_goto_function())
    python_code.append("")
    python_code.append("")

    # Register scenes
    python_code.append("# Register scenes")
    for scene_name in slab_files.keys():
        python_code.append(f"scenes['{scene_name}'] = scene_{scene_name}")
    python_code.append("")
    python_code.append("")

    # Add main entry
    python_code.append("# Start the app")
    python_code.append("root = tk.Tk()")
    python_code.append("root.title('Slab App')")
    python_code.append("root.geometry('400x300')")
    python_code.append("")
    python_code.append("goto('Main')")
    python_code.append("root.mainloop()")

    return "\n".join(python_code)


def compile_scene(name: str, tree: Node) -> list:
    """Compile a scene into a function."""
    lines = []
    lines.append(f"def scene_{name}():")
    lines.append(f'    """Scene: {name}"""')
    lines.append("    global current_window")
    lines.append("    ")
    lines.append("    # Clear current window")
    lines.append("    for widget in root.winfo_children():")
    lines.append("        widget.destroy()")
    lines.append("    ")

    for child in tree.children:
        if child.tag == "app":
            for window in child.children:
                if window.tag == "window":
                    title = window.attributes.get('title', name)
                    lines.append(f'    root.title("{title}")')
                    lines.append("    ")

                    for elem in window.children:
                        if elem.tag == "function":
                            continue  # already extracted
                        elem_lines = compile_element(elem)
                        for line in elem_lines:
                            lines.append(f"    {line}")

    return lines


def compile_element(node: Node) -> list:
    """Compile any element."""
    if node.tag == "text":
        return compile_text(node)
    elif node.tag == "button":
        return compile_button(node)
    elif node.tag == "input":
        return compile_input(node)
    elif node.tag == "box":
        return compile_box(node)
    elif node.tag == "row":
        return compile_layout(node, "row")
    elif node.tag == "column":
        return compile_layout(node, "column")
    elif node.tag == "background":
        return compile_background(node)
    elif node.tag == "image":
        return compile_image(node)
    return []


def compile_text(node: Node) -> list:
    """Compile a <text> element."""
    text = get_text(node)
    is_big = node.attributes.get('big', False)
    font_size = 16 if is_big else 12
    elem_id = node.attributes.get('id', None)

    lines = []
    if elem_id:
        # Store reference in global dict for later changes
        lines.append(f'texts["{elem_id}"] = tk.Label(root, text="{text}", font=({font_size}))')
        lines.append(f'texts["{elem_id}"].pack(padx=20, pady=5)')
    else:
        lines.append(f'tk.Label(root, text="{text}", font=({font_size})).pack(padx=20, pady=5)')
    return lines


def compile_background(node: Node) -> list:
    """Compile a <background color="..."/> element."""
    color = node.attributes.get('color', 'white')
    return [f'root.configure(bg="{color}")']


def compile_image(node: Node) -> list:
    """Compile an <image file="..."/> element with auto-sizing."""
    filepath = node.attributes.get('file', '')
    lines = []
    lines.append(f'if os.path.exists("{filepath}"):')
    lines.append(f'    _img = tk.PhotoImage(file="{filepath}")')
    # Auto-size: if image is bigger than 400px, scale it down
    lines.append(f'    while _img.width() > 400 or _img.height() > 400:')
    lines.append(f'        _img = _img.subsample(2, 2)')
    lines.append(f'    tk.Label(root, image=_img).pack(padx=10, pady=10)')
    lines.append(f'    root._img = _img  # keep reference')
    lines.append(f'else:')
    lines.append(f'    tk.Label(root, text="Image not found: {filepath}").pack()')
    return lines


def compile_button(node: Node) -> list:
    """Compile a <button> element."""
    text = get_text(node)
    onclick = node.attributes.get('onclick', '')

    lines = []
    if onclick.startswith("goto "):
        scene_name = onclick[5:].strip()
        lines.append(f'btn = tk.Button(root, text="{text}", command=lambda: goto("{scene_name}"))')
    elif onclick:
        lines.append(f'btn = tk.Button(root, text="{text}", command={onclick})')
    else:
        lines.append(f'btn = tk.Button(root, text="{text}")')

    lines.append("btn.pack(padx=20, pady=5)")
    return lines


def compile_input(node: Node) -> list:
    """Compile an <input> element."""
    lines = []
    lines.append("entry = tk.Entry(root, width=30)")
    lines.append("entry.pack(padx=20, pady=5)")
    return lines


def compile_box(node: Node) -> list:
    """Compile a <box> element."""
    lines = []
    lines.append("frame = tk.Frame(root)")
    lines.append('frame.pack(fill="both", expand=True, padx=10, pady=10)')

    for child in node.children:
        child_lines = compile_element(child)
        child_lines = [line.replace('root', 'frame') for line in child_lines]
        lines.extend(child_lines)

    return lines


def compile_layout(node: Node, direction: str) -> list:
    """Compile a <row> or <column>."""
    side = "left" if direction == "row" else "top"

    lines = []
    lines.append("frame = tk.Frame(root)")
    lines.append('frame.pack(fill="both", expand=True)')

    for child in node.children:
        child_lines = compile_element(child)
        child_lines = [line.replace('root', 'frame') for line in child_lines]
        for i, line in enumerate(child_lines):
            if '.pack(' in line and 'fill' not in line:
                child_lines[i] = line.replace('.pack(', f'.pack(side="{side}", ')
        lines.extend(child_lines)

    return lines


def compile_goto_function() -> list:
    """Compile the goto function."""
    return [
        "def goto(scene_name):",
        '    """Switch to a scene."""',
        "    if scene_name in scenes:",
        "        scenes[scene_name]()",
        "    else:",
        '        messagebox.showerror("Error", f"Scene {scene_name} not found!")',
    ]


# ---------------------------------------------------------------------------
# Single-file compiler (used by `slab run file.slab` when no project)
# ---------------------------------------------------------------------------

def compile_to_python(root: Node) -> str:
    """Compile a single .slab file into Python.

    Functions are emitted FIRST so they can be referenced by widgets.
    """
    python_code = [
        "import tkinter as tk",
        "from tkinter import messagebox",
        "import os",
        "",
        "# Text elements storage",
        "texts = {}",
        "",
        "# Variables storage",
        "vars = {}",
        "",
    ]

    # Pass 1 – collect all <function> blocks
    functions = []
    app_node = None
    for child in root.children:
        if child.tag == "function":
            functions.append(compile_function(child))
        elif child.tag == "app":
            app_node = child

    # Emit functions BEFORE any widgets
    for func in functions:
        python_code.append("")
        python_code.extend(func)

    # Pass 2 – compile the <app> / <window> widgets
    if app_node:
        for window in app_node.children:
            if window.tag == "window":
                python_code.append("")
                python_code.extend(_compile_window(window))

    python_code.append("")
    python_code.append("root.mainloop()")
    return "\n".join(python_code)


def _compile_window(node: Node) -> list:
    """Compile a <window> element."""
    lines = []
    title = node.attributes.get('title', 'Slab App')
    lines.append("")
    lines.append("root = tk.Tk()")
    lines.append(f'root.title("{title}")')
    lines.append("root.geometry('400x300')")

    for child in node.children:
        lines.append("")
        lines.extend(compile_element(child))

    return lines


def compile_function(node: Node) -> list:
    """Compile a <function> element."""
    name = node.attributes.get('name', 'unknown')
    lines = []
    lines.append(f"def {name}():")

    if not node.children:
        lines.append("    pass")
        return lines

    for child in node.children:
        action_lines = compile_action(child)
        for line in action_lines:
            lines.append(f"    {line}")

    return lines


def compile_action(node: Node) -> list:
    """Compile an action element."""
    if node.tag == "alert":
        message = node.attributes.get('message', 'Alert!')
        return [f'messagebox.showinfo("Alert", "{message}")']
    elif node.tag == "print":
        text = node.attributes.get('text', '')
        return [f'print("{text}")']
    elif node.tag == "set":
        name = node.attributes.get('name', 'var')
        value = node.attributes.get('to', '')
        return [f'{name} = "{value}"']
    elif node.tag == "setvar":
        name = node.attributes.get('name', 'var')
        value = node.attributes.get('value', '0')
        return [f'vars["{name}"] = {value}']
    elif node.tag == "change":
        text_id = node.attributes.get('textid', '')
        new_text = node.attributes.get('to', '')
        return [f'texts["{text_id}"].config(text="{new_text}")']
    elif node.tag == "close":
        return ["root.destroy()"]
    elif node.tag == "background":
        color = node.attributes.get('color', 'white')
        return [f'root.configure(bg="{color}")']
    elif node.tag == "if":
        return compile_if(node)
    elif node.tag in addons:
        attrs = dict(node.attributes)
        attrs_str = str(attrs)
        return [
            f'result = addon_funcs["{node.tag}"]({attrs_str})',
            f'if result: messagebox.showinfo("Addon", result)',
        ]
    return []


def compile_if(node: Node) -> list:
    """Compile an <if condition="..."> block."""
    condition = node.attributes.get('condition', 'True')
    lines = []
    lines.append(f"if {condition}:")
    if not node.children:
        lines.append("    pass")
    else:
        for child in node.children:
            action_lines = compile_action(child)
            for line in action_lines:
                lines.append(f"    {line}")
    return lines

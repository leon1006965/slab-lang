# Slab Programming Language - Development Plan

## Vision
A simple, HTML-like programming language for creating desktop apps. No complex syntax, no classes to remember - just structure and actions.

## Example Slab Code
```slab
<app>
  <window title="My First App">
    <text>Hello World!</text>
    <button onclick="greet">Click Me</button>
  </window>
</app>

<function name="greet">
  <alert message="Hello from Slab!"/>
</function>
```

## Key Principle: No Numbers!
- No width/height - Slab auto-sizes everything
- No font sizes - just `<text>` or `<text big>`
- No coordinates - layouts just work
- Like HTML: you say WHAT, not HOW

---

## Phase 1: Core Parser (Week 1)

### 1.1 File Structure
```
slab/
├── slab.py           # Main entry point
├── parser.py         # Parses .slab files
├── lexer.py          # Tokenizes the input
├── compiler.py       # Converts to Python
├── runtime.py        # Executes the app
├── elements/
│   ├── __init__.py
│   ├── window.py     # Window element
│   ├── button.py     # Button element
│   ├── text.py       # Text element
│   ├── input.py      # Input field
│   └── layout.py     # Box, Row, Column layouts
└── examples/
    └── hello.slab
```

### 1.2 Core Elements (No Numbers!)
1. `<app>` - Root element
2. `<window>` - Creates a window (just title, no size)
3. `<text>` - Displays text (use `<text big>` for large)
4. `<button>` - Clickable button
5. `<input>` - Text input field
6. `<box>`, `<row>`, `<column>` - Layout containers

### 1.3 Simple Actions
1. `<alert>` - Show popup: `<alert message="Hello!"/>`
2. `<set>` - Set variable: `<set name="x" to="hello"/>`
3. `<print>` - Print to console
4. `<get>` - Get input from user

---

## Phase 2: GUI Rendering (Week 2)

### 2.1 Technology Choice
- **Python + tkinter** - Built-in, simple, no extra installs
- Future: Could add PyQt or custom renderer

### 2.2 Element Mapping
| Slab Element | tkinter Widget |
|--------------|----------------|
| `<window>`   | `Tk()` or `Toplevel()` |
| `<text>`     | `Label` |
| `<button>`   | `Button` |
| `<input>`    | `Entry` |
| `<box>`      | `Frame` |
| `<row>`      | `Frame + pack(side=LEFT)` |
| `<column>`   | `Frame + pack(side=TOP)` |

---

## Phase 3: Actions & Logic (Week 3)

### 3.1 Simple Actions
```slab
<function name="greet">
  <alert message="Hello!"/>
  <set variable="name" value="Slab"/>
  <print text="User clicked button"/>
</function>
```

### 3.2 Conditional (Simple)
```slab
<if condition="name == 'Slab'">
  <alert message="Name is Slab!"/>
</if>
```

### 3.3 Loop (Simple)
```slab
<repeat times="3">
  <alert message="Hello!"/>
</repeat>
```

---

## Phase 4: Compiler to Python (Week 3-4)

### 4.1 Compilation Flow
```
.slab file → Parser → AST → Python code → tkinter app
```

### 4.2 Example Compilation
Input (hello.slab):
```slab
<app>
  <window title="Hello">
    <text>Hello!</text>
    <button onclick="greet">Click</button>
  </window>
</app>
<function name="greet">
  <alert message="Hi!"/>
</function>
```

Output (hello.py):
```python
import tkinter as tk
from tkinter import messagebox

def greet():
    messagebox.showinfo("Alert", "Hi!")

root = tk.Tk()
root.title("Hello")
# Auto-sized - no geometry needed!
label = tk.Label(root, text="Hello!")
label.pack(padx=20, pady=10)
button = tk.Button(root, text="Click", command=greet)
button.pack(padx=20, pady=10)
root.mainloop()
```

---

## Phase 5: CLI Tool (Week 4)

### 5.1 Commands
```bash
slab run app.slab      # Run the app
slab build app.slab    # Build to .py
slab new myapp         # Create new project
```

---

## Phase 6: Extension System (Future)

### 6.1 Addon Structure
```
addons/
├── my-addon/
│   ├── addon.json     # Name, version, author
│   ├── elements.py    # Custom elements
│   └── actions.py     # Custom actions
```

### 6.2 addon.json
```json
{
  "name": "my-addon",
  "version": "1.0",
  "author": "Developer",
  "elements": ["<my-button>"],
  "actions": ["<my-action>"]
}
```

---

## Implementation Order

1. **Step 1**: Create basic parser for HTML-like tags
2. **Step 2**: Map tags to tkinter widgets
3. **Step 3**: Add onclick and basic actions
4. **Step 4**: Create CLI to run .slab files
5. **Step 5**: Add more elements (input, layouts)
6. **Step 6**: Add variables and conditionals
7. **Step 7**: Add extension system

---

## Files to Create

1. `slab/slab.py` - Main CLI entry point
2. `slab/parser.py` - Parse .slab files
3. `slab/compiler.py` - Compile to Python
4. `slab/elements.py` - Element definitions
5. `slab/actions.py` - Action handlers
6. `slab/gui.py` - tkinter GUI renderer
7. `slab/examples/hello.slab` - Example app

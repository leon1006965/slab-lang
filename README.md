# Slab

**A simple programming language like HTML, but for desktop apps.**

No complex syntax. No remembering thousands of rules. Just structure and action.

```
<app>
  <window title="My App">
    <text big>Hello World!</text>
    <button onclick="greet">Click Me</button>
  </window>
</app>

<function name="greet">
  <alert message="Hello from Slab!"/>
</function>
```

---

## Quick Start

```bash
# Create a new project
./slab new myapp

# Run it
./slab run myapp/Main.slab

# Launch the IDE
./slab ide
```

---

## How to Code in Slab

### 1. Basic Structure

Every Slab app starts with `<app>` and has a `<window>`:

```slab
<app>
  <window title="My App">
    <!-- Your content here -->
  </window>
</app>
```

### 2. Adding Text

Use `<text>` for normal text or `<text big>` for large text:

```slab
<app>
  <window title="My App">
    <text big>This is big text</text>
    <text>This is normal text</text>
  </window>
</app>
```

### 3. Adding Buttons

Use `<button>` with `onclick` to make clickable buttons:

```slab
<app>
  <window title="My App">
    <text big>Click the button!</text>
    <button onclick="greet">Click Me</button>
  </window>
</app>

<function name="greet">
  <alert message="You clicked the button!"/>
</function>
```

### 4. Adding Input Fields

Use `<input>` to let users type text:

```slab
<app>
  <window title="My App">
    <text big>Enter your name:</text>
    <input/>
    <button onclick="submit">Submit</button>
  </window>
</app>

<function name="submit">
  <alert message="Thanks for entering your name!"/>
</function>
```

### 5. Organizing with Layouts

Use `<column>` for vertical layout or `<row>` for horizontal:

```slab
<app>
  <window title="My App">
    <column>
      <text>First item</text>
      <text>Second item</text>
      <text>Third item</text>
    </column>
  </window>
</app>
```

### 6. Actions

Actions are things that happen when you click buttons:

```slab
<function name="doSomething">
  <alert message="This pops up!"/>
  <print text="This goes to console"/>
  <set name="x" to="hello"/>
</function>
```

| Action | What it does |
|--------|--------------|
| `<alert message="..."/>` | Show a popup message |
| `<print text="..."/>` | Print to console |
| `<set name="x" to="..."/>` | Set a variable |

### 7. Scenes (Multiple Screens)

Create multiple `.slab` files and switch between them:

**Main.slab:**
```slab
<app>
  <window title="Main Menu">
    <text big>Welcome!</text>
    <button onclick="goto Scene1">Play Game</button>
    <button onclick="goto Scene2">Settings</button>
  </window>
</app>
```

**Scene1.slab:**
```slab
<app>
  <window title="Game">
    <text big>Playing the game!</text>
    <button onclick="goto Main">Back to Menu</button>
  </window>
</app>
```

Use `onclick="goto SceneName"` to switch scenes!

### 8. Using Addons

Addons let you extend Slab with extra features. Put addons in the `addons/` folder.

```slab
<function name="logAction">
  <log file="app.log" message="User clicked button"/>
  <encrypt file="secret.txt" password="mypass"/>
</function>
```

---

## Complete Example

```slab
<app>
  <window title="My Todo App">
    <text big>My Todo List</text>
    <column>
      <text>1. Learn Slab</text>
      <text>2. Build an app</text>
      <text>3. Share it</text>
    </column>
    <button onclick="addTodo">Add Todo</button>
    <button onclick="goto Settings">Settings</button>
  </window>
</app>

<function name="addTodo">
  <alert message="Todo added!"/>
</function>
```

---

## Commands

| Command | What it does |
|---------|--------------|
| `slab new <name>` | Create a new project |
| `slab run <file.slab>` | Run a Slab file |
| `slab build <file.slab>` | Build to Python |
| `slab ide` | Launch the IDE |

---

## Project Structure

```
myapp/
├── Main.slab        # Entry point (runs first)
├── Scene1.slab      # First scene
├── Scene2.slab      # Second scene
└── addons/          # Optional addons
    └── myaddon/
        ├── addon.json
        └── addon.py
```

---

## The Rules

1. **No numbers needed** - Slab auto-sizes everything
2. **Structure first** - Add `<app>`, `<window>`, then content
3. **Actions second** - Define `<function>` blocks for what buttons do
4. **Scenes** - Use `goto SceneName` to switch between screens

---

## License

MIT

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

### 6. Background Color

Set the window background with `<background>`:

```slab
<app>
  <window title="My App">
    <background color="blue"/>
    <text>Blue window!</text>
  </window>
</app>
```

### 7. Images

Show images with `<image>`. Images auto-size to fit:

```slab
<app>
  <window title="My App">
    <image file="photo.png"/>
  </window>
</app>
```

### 8. Text with IDs (Change Text Live)

Give text an `id` and change it later with `<change>`:

```slab
<app>
  <window title="Counter">
    <text id="counter" big>Count: 0</text>
    <button onclick="add">Add 1</button>
  </window>
</app>

<function name="add">
  <change textid="counter" to="Count: 1"/>
</function>
```

### 9. Variables

Store values with `<setvar>` and use them in checks:

```slab
<function name="start">
  <setvar name="score" value="0"/>
</function>
```

### 10. If Conditions

Check things with `<if>`:

```slab
<function name="check">
  <if condition="vars['score'] == 1">
    <alert message="You win!"/>
  </if>
</function>
```

### 11. Check/Case (Simple Switch)

Use `<check>` with `<case>` for easy value checking:

```slab
<function name="check">
  <setvar name="score" value="1"/>
  <check name="score">
    <case value="1" goto="WinScene"/>
    <case value="0" alert="Not eligible"/>
  </check>
</function>
```

### 12. Actions

Actions are things that happen when you click buttons:

```slab
<function name="doStuff">
  <alert message="This pops up!"/>
  <print text="This goes to console"/>
  <close/>
</function>
```

| Action | What it does |
|--------|--------------|
| `<alert message="..."/>` | Show a popup message |
| `<print text="..."/>` | Print to console |
| `<setvar name="x" value="..."/>` | Store a value |
| `<change textid="x" to="..."/>` | Change text on screen |
| `<background color="..."/>` | Change window color |
| `<close/>` | Close the app |

### 13. Scenes (Multiple Screens)

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

### 14. Using Addons

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
  <window title="My App">
    <background color="#222"/>
    <text id="score" big>Score: 0</text>
    <button onclick="addScore">Add Point</button>
    <button onclick="checkScore">Check Score</button>
    <button onclick="goto Scene2">Scene 2</button>
  </window>
</app>

<function name="addScore">
  <setvar name="score" value="1"/>
  <change textid="score" to="Score: 1"/>
</function>

<function name="checkScore">
  <check name="score">
    <case value="1" goto="Scene2"/>
    <case value="0" alert="Score is 0!"/>
  </check>
</function>
```

---

## Commands

| Command | What it does |
|---------|--------------|
| `slab new <name>` | Create a new project |
| `slab run <file.slab>` | Run a Slab file |
| `slab build <file.slab>` | Build to Python |
| `slab build-all <dir>` | Build entire project |
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
3. **Close tags in order** - Last opened, first closed
4. **Self-closing tags** - Use `/` at the end: `<alert message="Hi"/>`
5. **Functions** - Define `<function>` blocks for what buttons do
6. **Scenes** - Use `goto SceneName` to switch between screens

---

## License

MIT

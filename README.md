# Slab

A simple programming language like HTML, but for desktop apps.

## Quick Start

```bash
# Create a new app
./slab new myapp

# Run it
./slab run myapp/app.slab

# Build to Python
./slab build myapp/app.slab
```

## Example

```slab
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

## Elements

| Element | What it does |
|---------|--------------|
| `<app>` | Root element |
| `<window>` | Creates a window |
| `<text>` | Display text |
| `<text big>` | Large text |
| `<button>` | Clickable button |
| `<input>` | Text input |
| `<box>` | Container |
| `<row>` | Horizontal layout |
| `<column>` | Vertical layout |

## Actions

| Action | What it does |
|--------|--------------|
| `<alert message="..."/>` | Show popup |
| `<set name="x" to="..."/>` | Set variable |
| `<print text="..."/>` | Print to console |

## No Numbers!

Slab auto-sizes everything. Just say what you want:
- `<text>Hello</text>` - text appears
- `<button>Click</button>` - button appears
- No width, height, coordinates, or font sizes needed!

# Slab IDE - Scene System

## Vision
An IDE where you create apps with multiple scenes (like PocketCode).
- **Main.slab** - Entry point, runs first
- **Scene1.slab**, **Scene2.slab**, etc. - Different screens
- **goto Scene1** - Switch between scenes

## Example Structure

```
myapp/
├── Main.slab          # Starts here
├── Scene1.slab        # First scene
├── Scene2.slab        # Second scene
└── project.slab       # Project config (optional)
```

### Main.slab
```slab
<app>
  <window title="My Game">
    <text big>My Awesome Game</text>
    <button onclick="goto Scene1">Start Game</button>
    <button onclick="goto Scene2">Settings</button>
  </window>
</app>
```

### Scene1.slab
```slab
<app>
  <window title="Playing">
    <text>You are playing!</text>
    <button onclick="goto Main">Back to Menu</button>
    <button onclick="goto Scene2">Go to Settings</button>
  </window>
</app>
```

## IDE Features

### 1. File Panel (Left)
- Shows all .slab files in project
- Click to open in editor
- Right-click to rename/delete
- "New Scene" button

### 2. Code Editor (Center)
- Text editor for .slab files
- Syntax highlighting (simple)
- Line numbers

### 3. Toolbar (Top)
- **Run** button - Run the project
- **New Scene** button - Create SceneX.slab
- **Project name** display

### 4. Status Bar (Bottom)
- Shows current file
- Error messages

## Scene Switching Implementation

When compiler sees `onclick="goto Scene1"`:
1. Close current window
2. Parse Scene1.slab
3. Open new window with Scene1 content

### Generated Python:
```python
def goto_Scene1():
    root.destroy()
    # Load and run Scene1.slab
    import subprocess
    subprocess.run(['python3', 'slab.py', 'run', 'Scene1.slab'])
```

Or better - inline the scene code:
```python
def goto_Scene1():
    root.destroy()
    # [Compiled Scene1 code here]
```

## Files to Create

1. `ide/ide.py` - Main IDE window
2. `ide/editor.py` - Code editor widget
3. `ide/filepanel.py` - File tree panel
4. `ide/runner.py` - Run Slab projects
5. `ide/project.py` - Project management

## IDE Layout

```
+------------------------------------------+
|  [Run]  [New Scene]   My Game            |
+------------------------------------------+
| Files     |  Code Editor                 |
| --------- |  -------------------------  |
| Main.slab |  1: <app>                    |
| Scene1.slab| 2:   <window title="...">  |
| Scene2.slab| 3:     <text>Hello</text>  |
|           | 4:     <button onclick=...> |
| [+ Scene] | 5:   </window>              |
|           | 6: </app>                    |
+------------------------------------------+
|  Ready                                   |
+------------------------------------------+
```

## Implementation Steps

1. Create IDE window with tkinter
2. Add file panel with tree view
3. Add text editor with syntax highlighting
4. Add run functionality
5. Add "New Scene" button
6. Update compiler to handle `goto` scenes
7. Test with multi-scene project

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Node:
    tag: str
    attributes: dict = field(default_factory=dict)
    children: List['Node'] = field(default_factory=list)
    text: str = ""
    is_self_closing: bool = False


def parse_slab(code: str) -> Node:
    """Parse Slab code into a tree of Nodes."""
    code = code.strip()
    root = Node(tag="root")
    stack = [root]
    current = root
    
    i = 0
    while i < len(code):
        if code[i] == '<':
            # Find end of opening tag
            tag_end = code.index('>', i)
            tag_content = code[i+1:tag_end]
            
            # Self-closing tag
            if tag_content.endswith('/'):
                tag_content = tag_content[:-1]
                node = parse_tag(tag_content)
                current.children.append(node)
                i = tag_end + 1
                continue
            
            # Closing tag
            if tag_content.startswith('/'):
                tag_name = tag_content[1:].strip()
                if stack and stack[-1].tag == tag_name:
                    stack.pop()
                if stack:
                    current = stack[-1]
                i = tag_end + 1
                continue
            
            # Opening tag
            node = parse_tag(tag_content)
            current.children.append(node)
            stack.append(node)
            current = node
            i = tag_end + 1
            
            # Check for text content
            text_start = i
            while i < len(code) and code[i] != '<':
                i += 1
            text = code[text_start:i].strip()
            if text:
                current.text = text
        else:
            i += 1
    
    return root


def parse_tag(content: str) -> Node:
    """Parse a single tag into a Node."""
    # Handle quoted strings properly
    parts = []
    current = ""
    in_quotes = False
    quote_char = None
    
    for char in content:
        if char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
            current += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
            current += char
        elif char == ' ' and not in_quotes:
            if current:
                parts.append(current)
                current = ""
        else:
            current += char
    if current:
        parts.append(current)
    
    if not parts:
        return Node(tag="unknown")
    
    tag = parts[0]
    attributes = {}
    is_self_closing = content.endswith('/')
    
    # Parse attributes
    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=', 1)
            # Remove quotes
            value = value.strip('"').strip("'")
            attributes[key] = value
        else:
            # Boolean attribute like "big" on <text big>
            attributes[part] = True
    
    return Node(tag=tag, attributes=attributes, is_self_closing=is_self_closing)


def get_text(node: Node) -> str:
    """Get the text content of a node."""
    return node.text


def find_children(node: Node, tag: str) -> List[Node]:
    """Find all children with a specific tag."""
    return [child for child in node.children if child.tag == tag]


def find_child(node: Node, tag: str) -> Optional[Node]:
    """Find first child with a specific tag."""
    for child in node.children:
        if child.tag == tag:
            return child
    return None

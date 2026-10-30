"""Read-only, conservative stub observations; text matches are hints."""
from __future__ import annotations

import ast
import io
import os
import tokenize
import re
from pathlib import Path

EXCLUDED = {'.git', 'vendor', 'target', 'build', 'node_modules', 'tests', 'test', '__pycache__', '.venv'}
SUFFIXES = {'.py', '.rs', '.swift', '.dart', '.ts', '.tsx', '.js', '.jsx'}
MARKER = re.compile(r'\b(?:TODO\s*:\s*implement|STUB|Platzhalter)\b', re.I)
PATTERNS = {
    '.rs': re.compile(r'\b(?:todo|unimplemented)\s*!\s*\('),
    '.swift': re.compile(r'\bfatalError\s*\(\s*["\'](?:not implemented|unimplemented|todo)', re.I),
    '.dart': re.compile(r'\bthrow\s+(?:new\s+)?UnimplementedError\b'),
    '.ts': re.compile(r'\bthrow\s+.*(?:not implemented|unimplemented)', re.I),
    '.tsx': re.compile(r'\bthrow\s+.*(?:not implemented|unimplemented)', re.I),
    '.js': re.compile(r'\bthrow\s+.*(?:not implemented|unimplemented)', re.I),
    '.jsx': re.compile(r'\bthrow\s+.*(?:not implemented|unimplemented)', re.I),
}


def _name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return _name(node.func)
    return ''


def _python(text: str) -> list[tuple[int, str]]:
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return []
    found = []

    def visit(node: ast.AST, protocol: bool = False) -> None:
        if isinstance(node, ast.ClassDef):
            protocol = protocol or any(_name(base) == 'Protocol' for base in node.bases)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if protocol or any(_name(d) in {'abstractmethod', 'overload'} for d in node.decorator_list):
                return
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                body = body[1:]
            if len(body) == 1 and (isinstance(body[0], ast.Pass) or
                    isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and body[0].value.value is Ellipsis):
                found.append((body[0].lineno, 'empty_function'))
            for item in ast.walk(node):
                if isinstance(item, ast.Raise) and item.exc and _name(item.exc) == 'NotImplementedError':
                    found.append((item.lineno, 'not_implemented'))
            return
        for child in ast.iter_child_nodes(node):
            visit(child, protocol)
    visit(tree)
    return found


def scan(root: Path) -> list[dict]:
    """Scan production files without following symlinks or changing the repo."""
    root = Path(root)
    findings = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not (Path(directory) / d).is_symlink())
        for name in sorted(files):
            path = Path(directory) / name
            if path.suffix.lower() not in SUFFIXES or path.is_symlink() or name.startswith('test_') or name.endswith(('_test.py', '.generated.dart')):
                continue
            try:
                text = path.read_text(encoding='utf-8')
            except (OSError, UnicodeError):
                continue
            if re.search(r'@generated|generated file|do not edit', text[:500], re.I):
                continue
            relative = path.relative_to(root).as_posix()
            if path.suffix.lower() == '.py':
                findings.extend({'path': relative, 'line': line, 'regel': rule, 'sicherheit': 'sicher'} for line, rule in _python(text))
            pattern = PATTERNS.get(path.suffix.lower())
            if path.suffix.lower() == '.py':
                try:
                    lines = [(token.start[0], token.string) for token in tokenize.generate_tokens(io.StringIO(text).readline)
                             if token.type == tokenize.COMMENT]
                except (tokenize.TokenError, IndentationError):
                    lines = []
            else:
                lines = enumerate(text.splitlines(), 1)
            for number, line in lines:
                if MARKER.search(line) or (pattern and pattern.search(line)):
                    findings.append({'path': relative, 'line': number, 'regel': 'stub_marker', 'sicherheit': 'hinweis'})
    return findings

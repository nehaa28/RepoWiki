"""
File parser - extracts structure from individual files
"""

import ast
from pathlib import Path
from typing import Dict, List


class FileParser:
    """Parse individual code files and extract metadata"""

    def parse(self, file_path: Path) -> Dict:
        """
        Parse a single file and extract structure

        Returns:
            Dict containing:
                - path: File path
                - name: File name
                - extension: File extension
                - lines: Line count
                - imports: List of imports
                - classes: List of class definitions
                - functions: List of function definitions
                - comments: Extracted comments
        """
        file_path = Path(file_path)

        result = {
            'path': str(file_path),
            'name': file_path.name,
            'extension': file_path.suffix,
            'lines': 0,
            'docstring': '',
            'imports': [],
            'classes': [],
            'functions': [],
            'comments': []
        }

        # Read file
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                result['lines'] = len(content.splitlines())
        except Exception as e:
            result['error'] = str(e)
            return result

        # Parse based on extension
        if file_path.suffix == '.py':
            self._parse_python(content, result)
        # Add more parsers for other languages

        return result

    def _parse_python(self, content: str, result: Dict) -> None:
        """Parse Python file using AST"""
        try:
            tree = ast.parse(content)
            result['docstring'] = ast.get_docstring(tree) or ''

            for node in ast.iter_child_nodes(tree):
                # Extract imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        result['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    dots = '.' * node.level
                    result['imports'].append(dots + module)

                # Extract classes
                elif isinstance(node, ast.ClassDef):
                    methods = []
                    for item in ast.iter_child_nodes(node):
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            methods.append({
                                'name': item.name,
                                'args': [arg.arg for arg in item.args.args],
                                'docstring': ast.get_docstring(item) or ''
                            })
                    result['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'docstring': ast.get_docstring(node) or '',
                        'methods': methods
                    })

                # Extract top-level functions only
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    result['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node) or ''
                    })

        except SyntaxError as e:
            result['parse_error'] = str(e)

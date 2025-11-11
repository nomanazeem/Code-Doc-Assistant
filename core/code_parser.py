# core/code_parser.py
import ast
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from ..utils.file_utils import read_file, is_code_file

class CodeParser:
    """Enhanced code parser with support for multiple languages."""

    def __init__(self):
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c_header',
            '.hpp': 'cpp_header',
            '.rs': 'rust',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala'
        }

    def parse_codebase(self, codebase_path: str) -> Dict[str, Any]:
        """Parse entire codebase and extract structural information."""
        codebase_path = Path(codebase_path)
        if not codebase_path.exists():
            raise ValueError(f"Codebase path {codebase_path} does not exist")

        parsed_data = {
            'files': [],
            'functions': [],
            'classes': [],
            'imports': [],
            'file_structure': [],
            'summary': {
                'total_files': 0,
                'total_functions': 0,
                'total_classes': 0,
                'languages': set()
            }
        }

        for file_path in codebase_path.rglob('*'):
            if file_path.is_file() and self._is_supported_file(file_path):
                file_data = self._parse_file(file_path)
                if file_data:
                    parsed_data['files'].append(file_data)
                    parsed_data['summary']['languages'].add(file_data['language'])
                    parsed_data['summary']['total_files'] += 1

        # Update summary counts
        parsed_data['summary']['total_functions'] = len(parsed_data['functions'])
        parsed_data['summary']['total_classes'] = len(parsed_data['classes'])
        parsed_data['summary']['languages'] = list(parsed_data['summary']['languages'])

        return parsed_data

    def _is_supported_file(self, file_path: Path) -> bool:
        """Check if file extension is supported."""
        return file_path.suffix.lower() in self.supported_extensions

    def _parse_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse individual file and extract structural elements."""
        try:
            content = read_file(str(file_path))
            language = self.supported_extensions.get(file_path.suffix.lower())

            file_data = {
                'path': str(file_path),
                'name': file_path.name,
                'language': language,
                'size': len(content),
                'line_count': len(content.splitlines()),
                'content': content
            }

            # Language-specific parsing
            if language == 'python':
                self._parse_python_file(content, file_path, file_data)
            # Add other language parsers here as needed

            return file_data

        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return None

    def _parse_python_file(self, content: str, file_path: Path, file_data: Dict[str, Any]):
        """Parse Python file using AST."""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_data = self._extract_function_data(node, file_path)
                    file_data.setdefault('functions', []).append(function_data)

                elif isinstance(node, ast.ClassDef):
                    class_data = self._extract_class_data(node, file_path)
                    file_data.setdefault('classes', []).append(class_data)

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_data = self._extract_import_data(node)
                    file_data.setdefault('imports', []).append(import_data)

        except SyntaxError as e:
            print(f"Syntax error in Python file {file_path}: {e}")

    def _extract_function_data(self, node: ast.FunctionDef, file_path: Path) -> Dict[str, Any]:
        """Extract function information from AST node."""
        args = [arg.arg for arg in node.args.args]
        returns = None

        if node.returns:
            returns = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)

        return {
            'name': node.name,
            'file_path': str(file_path),
            'line_start': node.lineno,
            'line_end': getattr(node, 'end_lineno', node.lineno),
            'args': args,
            'returns': returns,
            'docstring': ast.get_docstring(node),
            'type': 'function',
            'decorators': [ast.unparse(decorator) for decorator in node.decorator_list]
                         if hasattr(ast, 'unparse') else []
        }

    def _extract_class_data(self, node: ast.ClassDef, file_path: Path) -> Dict[str, Any]:
        """Extract class information from AST node."""
        methods = []
        class_variables = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
            elif isinstance(item, ast.Assign):
                # Extract class variables
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_variables.append(target.id)

        return {
            'name': node.name,
            'file_path': str(file_path),
            'line_start': node.lineno,
            'line_end': getattr(node, 'end_lineno', node.lineno),
            'docstring': ast.get_docstring(node),
            'methods': methods,
            'class_variables': class_variables,
            'type': 'class',
            'decorators': [ast.unparse(decorator) for decorator in node.decorator_list]
                         if hasattr(ast, 'unparse') else []
        }

    def _extract_import_data(self, node: ast.AST) -> Dict[str, Any]:
        """Extract import information from AST node."""
        if isinstance(node, ast.Import):
            return {
                'type': 'import',
                'modules': [alias.name for alias in node.names],
                'names': [alias.asname or alias.name for alias in node.names]
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                'type': 'import_from',
                'module': node.module,
                'level': node.level,
                'names': [alias.name for alias in node.names],
                'aliases': [alias.asname for alias in node.names if alias.asname]
            }
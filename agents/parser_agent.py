# agents/parser_agent.py
import ast
import os
from typing import Dict, List, Any
from pathlib import Path
import tree_sitter
from tree_sitter_languages import get_language, get_parser

class ParserAgent:
    def __init__(self):
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rs': 'rust',
            '.go': 'go'
        }

    def parse_codebase(self, codebase_path: str) -> Dict[str, Any]:
        """Parse the entire codebase and extract structural information."""
        codebase_path = Path(codebase_path)
        if not codebase_path.exists():
            raise ValueError(f"Codebase path {codebase_path} does not exist")

        parsed_data = {
            'files': [],
            'functions': [],
            'classes': [],
            'imports': [],
            'file_structure': []
        }

        for file_path in codebase_path.rglob('*'):
            if file_path.is_file() and self._is_supported_file(file_path):
                file_data = self._parse_file(file_path)
                parsed_data['files'].append(file_data)

                # Extract functions and classes
                if file_data.get('language') == 'python':
                    self._extract_python_elements(file_path, parsed_data)
                else:
                    self._extract_generic_elements(file_path, parsed_data)

        return parsed_data

    def _is_supported_file(self, file_path: Path) -> bool:
        return file_path.suffix in self.supported_extensions

    def _parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse individual file and extract basic information."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            language = self.supported_extensions.get(file_path.suffix)

            return {
                'path': str(file_path),
                'name': file_path.name,
                'language': language,
                'size': len(content),
                'line_count': len(content.splitlines()),
                'content': content
            }
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return {}

    def _extract_python_elements(self, file_path: Path, parsed_data: Dict[str, Any]):
        """Extract functions and classes from Python files using AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_data = {
                        'name': node.name,
                        'file_path': str(file_path),
                        'line_start': node.lineno,
                        'line_end': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node),
                        'type': 'function'
                    }
                    parsed_data['functions'].append(function_data)

                elif isinstance(node, ast.ClassDef):
                    class_data = {
                        'name': node.name,
                        'file_path': str(file_path),
                        'line_start': node.lineno,
                        'line_end': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                        'docstring': ast.get_docstring(node),
                        'methods': [],
                        'type': 'class'
                    }

                    # Extract methods from class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_data['methods'].append(item.name)

                    parsed_data['classes'].append(class_data)

        except Exception as e:
            print(f"Error extracting Python elements from {file_path}: {e}")

    def _extract_generic_elements(self, file_path: Path, parsed_data: Dict[str, Any]):
        """Extract elements from non-Python files using tree-sitter."""
        # Implementation for other languages would go here
        # This is a simplified version
        pass
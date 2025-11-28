import ast
import os
import pickle
from pathlib import Path
from typing import Dict, List, Any
from sentence_transformers import SentenceTransformer

class ParserAgent:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a Python file and extract code structure using AST"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            return self._parse_with_ast(file_path, content)
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return self._fallback_parsing(file_path, content)
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return {}

    def _parse_with_ast(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse using Python's built-in AST"""
        tree = ast.parse(content)

        elements = []

        for node in ast.walk(tree):
            element_info = {}

            if isinstance(node, ast.FunctionDef):
                element_info = {
                    'type': 'function',
                    'name': node.name,
                    'line_start': node.lineno,
                    'docstring': ast.get_docstring(node),
                    'signature': self._extract_function_signature(node),
                    'args': [arg.arg for arg in node.args.args],
                    'returns': bool(node.returns)
                }
            elif isinstance(node, ast.ClassDef):
                element_info = {
                    'type': 'class',
                    'name': node.name,
                    'line_start': node.lineno,
                    'docstring': ast.get_docstring(node),
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                }
            elif isinstance(node, ast.Module):
                element_info = {
                    'type': 'module',
                    'docstring': ast.get_docstring(node)
                }
            elif isinstance(node, ast.AsyncFunctionDef):
                element_info = {
                    'type': 'async_function',
                    'name': node.name,
                    'line_start': node.lineno,
                    'docstring': ast.get_docstring(node),
                    'signature': self._extract_function_signature(node),
                    'args': [arg.arg for arg in node.args.args],
                    'returns': bool(node.returns)
                }

            if element_info:
                element_info['file_path'] = file_path
                element_info['content_snippet'] = self._get_content_snippet(content, element_info.get('line_start', 1))
                elements.append(element_info)

        return {
            'file_path': file_path,
            'elements': elements,
            'total_elements': len(elements)
        }

    def _fallback_parsing(self, file_path: str, content: str) -> Dict[str, Any]:
        """Fallback parsing for files with syntax errors"""
        elements = []
        lines = content.split('\n')

        # Simple regex-based parsing as fallback
        import re

        # Look for function definitions
        func_pattern = r'^def\s+(\w+)\s*\('
        class_pattern = r'^class\s+(\w+)'

        for i, line in enumerate(lines):
            func_match = re.match(func_pattern, line.strip())
            class_match = re.match(class_pattern, line.strip())

            if func_match:
                element_info = {
                    'type': 'function',
                    'name': func_match.group(1),
                    'line_start': i + 1,
                    'file_path': file_path,
                    'content_snippet': self._get_content_snippet(content, i + 1)
                }
                elements.append(element_info)

            elif class_match:
                element_info = {
                    'type': 'class',
                    'name': class_match.group(1),
                    'line_start': i + 1,
                    'file_path': file_path,
                    'content_snippet': self._get_content_snippet(content, i + 1)
                }
                elements.append(element_info)

        return {
            'file_path': file_path,
            'elements': elements,
            'total_elements': len(elements)
        }

    def _extract_function_signature(self, node) -> str:
        """Extract function signature from AST node"""
        args = [arg.arg for arg in node.args.args]
        return f"{node.name}({', '.join(args)})"

    def _get_content_snippet(self, content: str, line_start: int) -> str:
        """Get a snippet of content around the specified line"""
        lines = content.split('\n')
        start = max(0, line_start - 2)
        end = min(len(lines), line_start + 8)
        return '\n'.join(lines[start:end])

    def index_codebase(self, codebase_path: str, index_path: str) -> bool:
        """Index the entire codebase"""
        try:
            python_files = list(Path(codebase_path).rglob("*.py"))
            all_elements = []

            for file_path in python_files:
                parsed_data = self.parse_file(str(file_path))
                all_elements.extend(parsed_data.get('elements', []))

            # Create embeddings for all elements
            texts_to_embed = []
            for elem in all_elements:
                text = f"{elem['type']} {elem['name']}"
                if 'signature' in elem:
                    text += f" {elem['signature']}"
                if 'content_snippet' in elem:
                    text += f": {elem['content_snippet'][:300]}"
                texts_to_embed.append(text)

            embeddings = self.embedding_model.encode(texts_to_embed)

            # Save index
            os.makedirs(index_path, exist_ok=True)

            index_data = {
                'elements': all_elements,
                'embeddings': embeddings,
                'metadata': {
                    'total_files': len(python_files),
                    'total_elements': len(all_elements)
                }
            }

            with open(os.path.join(index_path, 'code_index.pkl'), 'wb') as f:
                pickle.dump(index_data, f)

            print(f"✅ Indexed {len(python_files)} files with {len(all_elements)} elements")
            return True

        except Exception as e:
            print(f"❌ Error indexing codebase: {e}")
            return False
    
    def analyze_documentation_quality(self, codebase_path: str) -> Dict[str, Any]:
        """Analyze documentation quality across the codebase"""
        python_files = list(Path(codebase_path).rglob("*.py"))
        total_files = len(python_files)
        files_with_docs = 0
        docstring_quality_scores = []
        
        for file_path in python_files:
            parsed_data = self.parse_file(str(file_path))
            elements = parsed_data.get('elements', [])
            
            file_has_docs = any(elem.get('docstring') for elem in elements)
            if file_has_docs:
                files_with_docs += 1
            
            for elem in elements:
                if elem.get('docstring'):
                    quality_score = self._rate_docstring_quality(elem['docstring'])
                    docstring_quality_scores.append(quality_score)
        
        avg_quality = sum(docstring_quality_scores) / len(docstring_quality_scores) if docstring_quality_scores else 0
        
        return {
            'total_files': total_files,
            'files_with_docs': files_with_docs,
            'coverage_percentage': (files_with_docs / total_files * 100) if total_files > 0 else 0,
            'avg_docstring_quality': avg_quality
        }
    
    def _rate_docstring_quality(self, docstring: str) -> float:
        """Rate docstring quality on a scale of 1-10"""
        if not docstring:
            return 0
        
        score = 0
        lines = docstring.strip().split('\n')
        
        # Check for description
        if len(lines) >= 1 and len(lines[0].strip()) > 10:
            score += 3
        
        # Check for parameter documentation
        if any('param' in line.lower() or 'argument' in line.lower() for line in lines):
            score += 3
        
        # Check for return value documentation
        if any('return' in line.lower() or 'returns' in line.lower() for line in lines):
            score += 2
        
        # Check for examples
        if any('example' in line.lower() or '>>>' in line for line in lines):
            score += 2
        
        return min(10, score)
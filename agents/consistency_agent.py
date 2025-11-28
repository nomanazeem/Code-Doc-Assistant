import ast
import re
from typing import Dict, List, Tuple

class ConsistencyAgent:
    def __init__(self):
        self.docstring_styles = ['google', 'numpy', 'sphinx']
    
    def check_consistency(self, file_path: str, documented_code: str) -> str:
        """Check documentation consistency and return recommendations"""
        issues = []
        
        try:
            tree = ast.parse(documented_code)
            
            # Check module-level docstring
            module_docstring = ast.get_docstring(tree)
            if not module_docstring:
                issues.append("Missing module-level docstring")
            
            # Check function and class docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    docstring = ast.get_docstring(node)
                    
                    if not docstring:
                        issues.append(f"Missing docstring for {node.name}")
                    else:
                        style_issues = self._check_docstring_style(docstring, node.name)
                        issues.extend(style_issues)
            
            # Check naming conventions
            naming_issues = self._check_naming_conventions(tree)
            issues.extend(naming_issues)
            
            # Check comment consistency
            comment_issues = self._check_comment_consistency(documented_code)
            issues.extend(comment_issues)
            
        except SyntaxError as e:
            issues.append(f"Syntax error in generated code: {e}")
        
        return "; ".join(issues) if issues else "All checks passed"
    
    def _check_docstring_style(self, docstring: str, element_name: str) -> List[str]:
        """Check docstring style consistency"""
        issues = []
        lines = docstring.split('\n')
        
        # Check for common sections
        has_params = any(re.search(r'param|args?|attributes?', line, re.I) for line in lines)
        has_returns = any(re.search(r'return|returns', line, re.I) for line in lines)
        has_raises = any(re.search(r'raise|raises|except', line, re.I) for line in lines)
        
        if not has_params and 'test' not in element_name.lower():
            issues.append(f"Docstring for {element_name} might be missing parameter documentation")
        
        if not has_returns and not element_name.startswith('__init__'):
            issues.append(f"Docstring for {element_name} might be missing return documentation")
        
        # Check for consistent formatting
        if len(lines) > 1 and lines[1].strip():  # Second line should be empty in multi-line docstrings
            issues.append(f"Docstring for {element_name} might have incorrect formatting")
        
        return issues
    
    def _check_naming_conventions(self, tree: ast.AST) -> List[str]:
        """Check Python naming conventions"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name[0].isupper() or '_' in node.name:
                    issues.append(f"Class name '{node.name}' should use CamelCase")
            
            elif isinstance(node, ast.FunctionDef):
                if not node.name.replace('_', '').islower():
                    issues.append(f"Function name '{node.name}' should use snake_case")
                
                # Check for single letter variables in function parameters
                for arg in node.args.args:
                    if len(arg.arg) == 1 and arg.arg != 'self':
                        issues.append(f"Single-letter parameter '{arg.arg}' in function '{node.name}'")
        
        return issues
    
    def _check_comment_consistency(self, code: str) -> List[str]:
        """Check comment style consistency"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            
            # Check for TODO, FIXME, etc. without explanations
            if re.search(r'\b(TODO|FIXME|XXX|HACK)\b', line, re.I) and not re.search(r'\b(TODO|FIXME|XXX|HACK)\b.*:', line, re.I):
                issues.append(f"Unclear TODO/FIXME at line {i+1}: add explanation")
            
            # Check for commented code
            if stripped_line.startswith('#') and len(stripped_line) > 2:
                commented_content = stripped_line[1:].strip()
                if (commented_content[0].isalpha() or commented_content.startswith('[') or 
                    commented_content.startswith('{') or '=' in commented_content):
                    issues.append(f"Possible commented code at line {i+1}")
        
        return issues
    
    def suggest_improvements(self, file_path: str, documented_code: str) -> List[str]:
        """Suggest specific improvements for documentation"""
        improvements = []
        
        try:
            tree = ast.parse(documented_code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    docstring = ast.get_docstring(node)
                    
                    if docstring:
                        # Check docstring completeness
                        if len(docstring.split()) < 10:  # Very short docstring
                            improvements.append(f"Consider expanding docstring for {node.name}")
                        
                        # Check for examples
                        if 'example' not in docstring.lower() and '>>>' not in docstring:
                            improvements.append(f"Add usage example to {node.name} docstring")
                
                # Check for type hints
                if isinstance(node, ast.FunctionDef):
                    if not node.returns:
                        improvements.append(f"Add return type hint to {node.name}")
                    
                    for arg in node.args.args:
                        if not arg.annotation:
                            improvements.append(f"Add type hint for parameter '{arg.arg}' in {node.name}")
        
        except SyntaxError:
            improvements.append("Fix syntax errors before further improvements")
        
        return improvements
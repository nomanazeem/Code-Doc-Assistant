# agents/consistency_agent.py
import re
from typing import Dict, List, Any

class ConsistencyAgent:
    def __init__(self):
        self.style_patterns = {
            'python': {
                'docstring_style': r'\"\"\"(.+?)\"\"\"|\'\'\'(.+?)\'\'\'',
                'function_pattern': r'def\s+(\w+)\s*\(',
                'class_pattern': r'class\s+(\w+)'
            }
        }

    def analyze_consistency(self, parsed_data: Dict[str, Any], generated_docs: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze consistency of generated documentation with existing codebase."""
        analysis = {
            'style_issues': [],
            'formatting_issues': [],
            'coverage_issues': [],
            'recommendations': []
        }

        # Check docstring style consistency
        self._check_style_consistency(parsed_data, analysis)

        # Check formatting patterns
        self._check_formatting_consistency(generated_docs, analysis)

        # Check documentation coverage
        self._check_coverage(parsed_data, analysis)

        return analysis

    def _check_style_consistency(self, parsed_data: Dict[str, Any], analysis: Dict[str, Any]):
        """Check for consistent documentation styles across the codebase."""
        docstring_styles = set()

        for func in parsed_data.get('functions', []):
            docstring = func.get('docstring', '')
            if docstring and docstring != 'None':
                style = self._detect_docstring_style(docstring)
                docstring_styles.add(style)

        if len(docstring_styles) > 1:
            analysis['style_issues'].append(
                f"Multiple docstring styles detected: {', '.join(docstring_styles)}"
            )

    def _detect_docstring_style(self, docstring: str) -> str:
        """Detect the style of a docstring."""
        if docstring.startswith('"""') and docstring.endswith('"""'):
            return 'triple-double-quotes'
        elif docstring.startswith("'''") and docstring.endswith("'''"):
            return 'triple-single-quotes'
        else:
            return 'unknown'

    def _check_formatting_consistency(self, generated_docs: Dict[str, Any], analysis: Dict[str, Any]):
        """Check formatting consistency in generated documentation."""
        # Check for consistent parameter formatting
        for func_doc in generated_docs.get('functions', []):
            docstring = func_doc.get('generated_doc', '')
            if not self._has_parameter_sections(docstring):
                analysis['formatting_issues'].append(
                    f"Function {func_doc['element']['name']}: Missing parameter section"
                )

    def _has_parameter_sections(self, docstring: str) -> bool:
        """Check if docstring has proper parameter sections."""
        param_keywords = ['param', 'argument', 'args:', 'parameters:']
        return any(keyword in docstring.lower() for keyword in param_keywords)

    def _check_coverage(self, parsed_data: Dict[str, Any], analysis: Dict[str, Any]):
        """Check documentation coverage across the codebase."""
        total_functions = len(parsed_data.get('functions', []))
        documented_functions = sum(1 for f in parsed_data.get('functions', [])
                                 if f.get('docstring') and f['docstring'] != 'None')

        total_classes = len(parsed_data.get('classes', []))
        documented_classes = sum(1 for c in parsed_data.get('classes', [])
                               if c.get('docstring') and c['docstring'] != 'None')

        if total_functions > 0:
            func_coverage = (documented_functions / total_functions) * 100
            analysis['coverage_issues'].append(
                f"Function documentation coverage: {func_coverage:.1f}%"
            )

        if total_classes > 0:
            class_coverage = (documented_classes / total_classes) * 100
            analysis['coverage_issues'].append(
                f"Class documentation coverage: {class_coverage:.1f}%"
            )
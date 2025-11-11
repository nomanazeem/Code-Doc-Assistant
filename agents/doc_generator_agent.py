# agents/doc_generator_agent.py
from typing import Dict, List, Any
from ..core.rag_pipeline import RAGPipeline

class DocumentationGeneratorAgent:
    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag_pipeline = rag_pipeline
        self.generated_docs = []

    def generate_docstrings(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate docstrings for all code elements."""
        results = {
            'functions': [],
            'classes': [],
            'files': []
        }

        # Generate docstrings for functions
        for func in parsed_data.get('functions', []):
            if not func.get('docstring') or self._needs_improvement(func.get('docstring', '')):
                docstring = self.rag_pipeline.generate_documentation(func)
                results['functions'].append({
                    'element': func,
                    'generated_doc': docstring,
                    'existing_doc': func.get('docstring', 'None')
                })

        # Generate docstrings for classes
        for cls in parsed_data.get('classes', []):
            if not cls.get('docstring') or self._needs_improvement(cls.get('docstring', '')):
                docstring = self.rag_pipeline.generate_documentation(cls)
                results['classes'].append({
                    'element': cls,
                    'generated_doc': docstring,
                    'existing_doc': cls.get('docstring', 'None')
                })

        self.generated_docs = results
        return results

    def _needs_improvement(self, docstring: str) -> bool:
        """Check if existing documentation needs improvement."""
        if not docstring or docstring == 'None':
            return True

        # Simple heuristic: if docstring is very short or generic
        short_phrases = ['todo', 'implement', 'add documentation', '...']
        doc_lower = docstring.lower()

        return (len(docstring.strip()) < 20 or
                any(phrase in doc_lower for phrase in short_phrases))

    def apply_documentation(self, output_dir: str = None):
        """Apply generated documentation to the code files."""
        # This would implement the logic to modify source files
        # with the generated documentation
        pass
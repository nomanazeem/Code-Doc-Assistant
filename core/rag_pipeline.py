# core/rag_pipeline.py
from typing import List, Dict, Any
import openai
from .vector_store import CodeVectorStore

class RAGPipeline:
    def __init__(self, vector_store: CodeVectorStore, openai_api_key: str = None):
        self.vector_store = vector_store
        if openai_api_key:
            openai.api_key = openai_api_key

    def generate_documentation(self, code_element: Dict[str, Any], context_elements: List[Dict[str, Any]] = None) -> str:
        """Generate documentation using RAG approach."""

        # Build context from similar code elements
        context = self._build_context(code_element, context_elements)

        prompt = self._create_documentation_prompt(code_element, context)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert code documentation assistant. Generate clear, concise, and helpful documentation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating documentation: {e}"

    def _build_context(self, target_element: Dict[str, Any], context_elements: List[Dict[str, Any]] = None) -> str:
        """Build context from similar code elements."""
        context_parts = []

        # Use provided context elements or search for similar ones
        if context_elements is None:
            query = f"{target_element.get('type', 'element')} {target_element.get('name', '')}"
            similar_elements = self.vector_store.search_similar(query, k=3)
            context_elements = [elem['metadata'] for elem in similar_elements]

        for elem in context_elements:
            if elem.get('docstring'):
                context_parts.append(f"Similar {elem['type']} '{elem['name']}': {elem['docstring']}")

        return "\n".join(context_parts)

    def _create_documentation_prompt(self, code_element: Dict[str, Any], context: str) -> str:
        """Create a prompt for documentation generation."""
        element_type = code_element.get('type', 'element')
        name = code_element.get('name', 'Unknown')
        file_path = code_element.get('file_path', 'Unknown')
        args = code_element.get('args', [])
        existing_doc = code_element.get('docstring', 'None')

        prompt = f"""
        Please generate comprehensive documentation for the following {element_type}:

        {element_type.capitalize()} Name: {name}
        File: {file_path}
        Arguments: {', '.join(args)}
        Existing Documentation: {existing_doc}

        Context from similar code elements:
        {context}

        Please generate:
        1. A clear docstring following the appropriate style guide
        2. Brief explanation of purpose
        3. Parameter descriptions (if applicable)
        4. Return value description (if applicable)
        5. Any important notes or examples

        Make the documentation consistent with the existing style in the codebase.
        """

        return prompt
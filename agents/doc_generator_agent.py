import google.generativeai as genai
import os
from typing import Dict, List, Optional
from pathlib import Path

class DocumentationGeneratorAgent:
    def __init__(self, rag_pipeline):
        self.rag_pipeline = rag_pipeline
        self.model = self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini model"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        
        # Use gemini-1.5-pro for better code understanding
        model = genai.GenerativeModel('gemini-1.5-pro')
        return model
    
    def generate_documentation(self, file_path: str) -> str:
        """Generate documentation for a file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
        
        # Get relevant context from RAG pipeline
        relevant_context = self.rag_pipeline.get_relevant_context(file_path, code_content)
        
        # Generate documentation using Gemini
        prompt = self._create_documentation_prompt(code_content, relevant_context)
        
        try:
            response = self.model.generate_content(prompt)
            documented_code = response.text
            
            # Extract code from response (Gemini might add explanations)
            if "```python" in documented_code:
                documented_code = documented_code.split("```python")[1].split("```")[0]
            elif "```" in documented_code:
                documented_code = documented_code.split("```")[1].split("```")[0]
            
            return documented_code.strip()
            
        except Exception as e:
            print(f"Error generating documentation: {e}")
            return code_content  # Return original code if generation fails
    
    def _create_documentation_prompt(self, code_content: str, context: List[Dict]) -> str:
        """Create prompt for documentation generation"""
        context_str = "\n".join([
            f"Related {ctx['type']} {ctx['name']}: {ctx.get('content_snippet', '')[:200]}..."
            for ctx in context[:3]  # Use top 3 most relevant contexts
        ])
        
        prompt = f"""
        You are a expert Python documentation generator. Your task is to add comprehensive documentation to the following Python code.
        
        CONTEXT FROM CODEBASE:
        {context_str}
        
        CODE TO DOCUMENT:
        ```python
        {code_content}
        ```
        
        Please generate the documented version of this code with:
        1. Module-level docstring if missing
        2. Class docstrings following Google-style or NumPy-style
        3. Function/method docstrings with parameters, return values, and exceptions
        4. Inline comments for complex logic
        5. Type hints if missing
        
        Guidelines:
        - Maintain the exact same code functionality
        - Use appropriate docstring style based on existing patterns
        - Keep comments concise and meaningful
        - Add type hints where beneficial
        - Preserve all existing code and comments
        
        Return ONLY the complete documented Python code without any additional explanations.
        """
        
        return prompt
    
    def improve_existing_docstring(self, element_info: Dict) -> str:
        """Improve an existing docstring"""
        prompt = f"""
        Improve the following code element's documentation:
        
        Element: {element_info['type']} {element_info['name']}
        Current Code: {element_info.get('content_snippet', '')}
        Current Docstring: {element_info.get('docstring', 'None')}
        
        Please provide an improved docstring following best practices. Focus on:
        - Clear description of purpose
        - Comprehensive parameter documentation
        - Return value explanation
        - Example usage if helpful
        - Exception documentation
        
        Return ONLY the improved docstring text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error improving docstring: {e}")
            return element_info.get('docstring', '')
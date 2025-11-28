#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path
import datetime

class FixedDocGenerator:
    """Fixed documentation generator with better error handling"""

    def __init__(self):
        self.use_gemini = False
        try:
            import google.generativeai as genai
            from dotenv import load_dotenv
            load_dotenv()

            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                # Test the API connection
                self.model = genai.GenerativeModel('gemini-pro')
                # Simple test to verify API works
                test_response = self.model.generate_content("Say hello")
                if test_response.text:
                    self.use_gemini = True
                    print("✅ Gemini API connected successfully")
                else:
                    print("⚠️  Gemini API test failed, using local templates")
            else:
                print("⚠️  No Gemini API key found, using local templates")

        except Exception as e:
            print(f"⚠️  Gemini not available: {e}, using local templates")

    def generate_documentation(self, file_path, preview=False):
        """Generate documentation with proper error handling"""
        print(f"📄 Processing: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            if self.use_gemini:
                documented_content = self._generate_with_gemini(original_content)
                # Validate that we didn't get the prompt back
                if "{code}" in documented_content or "CODE TO DOCUMENT" in documented_content:
                    print("  ⚠️  Gemini returned prompt instead of code, using local method")
                    documented_content = self._generate_local(original_content, file_path)
            else:
                documented_content = self._generate_local(original_content, file_path)

            if preview:
                self._show_preview(original_content, documented_content)
                return True
            else:
                # Create backup first
                backup_path = f"{file_path}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)

                # Write documented version
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(documented_content)

                print(f"  ✅ Documentation added (backup: {os.path.basename(backup_path)})")
                return True

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    def _generate_with_gemini(self, content):
        """Generate documentation using Gemini with better prompt"""
        try:
            # Cleaner, more specific prompt
            prompt = f"""Please add comprehensive documentation to this Python code.

Add:
1. Module docstring if missing
2. Class docstrings with Google style
3. Function docstrings with parameters, returns, and examples
4. Keep all existing code and functionality

Return ONLY the complete Python code with documentation, no explanations.

Code:
{content}"""

            response = self.model.generate_content(prompt)
            result = response.text.strip()

            # Better cleaning of response
            if "```python" in result:
                result = result.split("```python")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()

            # Validate result
            if not result or result == content:
                raise ValueError("No changes made by Gemini")

            return result

        except Exception as e:
            print(f"    Gemini error: {e}")
            raise

    def _generate_local(self, content, file_path):
        """Generate basic documentation using reliable local method"""
        lines = content.split('\n')
        output_lines = []
        i = 0

        # Preserve shebang and encoding comments
        while i < len(lines) and (lines[i].startswith('#!') or lines[i].startswith('# -*-')):
            output_lines.append(lines[i])
            i += 1

        # Add module docstring if missing (only if we're at the beginning)
        if i == 0 or (i == 1 and output_lines and output_lines[0].startswith('#!')):
            has_docstring = False
            # Check if there's already a docstring in the next few lines
            for j in range(i, min(i+5, len(lines))):
                if lines[j].strip().startswith('"""') or lines[j].strip().startswith("'''"):
                    has_docstring = True
                    break
                if lines[j].strip() and not lines[j].startswith('#') and not lines[j].startswith('import'):
                    break

            if not has_docstring:
                module_doc = f'"""{os.path.basename(file_path)}\n\nModule description.\n"""'
                output_lines.append(module_doc)
                output_lines.append('')

        # Process the rest of the file
        while i < len(lines):
            current_line = lines[i]
            output_lines.append(current_line)

            # Check for function definitions
            if current_line.strip().startswith('def '):
                func_name = self._extract_function_name(current_line)
                if func_name and not self._next_line_has_docstring(lines, i):
                    # Add function docstring
                    docstring = self._create_function_docstring(func_name, current_line)
                    output_lines.append('    """' + docstring + '"""')

            # Check for class definitions
            elif current_line.strip().startswith('class '):
                class_name = self._extract_class_name(current_line)
                if class_name and not self._next_line_has_docstring(lines, i):
                    # Add class docstring
                    docstring = self._create_class_docstring(class_name)
                    output_lines.append('    """' + docstring + '"""')

            i += 1

        return '\n'.join(output_lines)

    def _next_line_has_docstring(self, lines, current_index):
        """Check if the next line after current_index has a docstring"""
        if current_index + 1 >= len(lines):
            return False

        next_line = lines[current_index + 1].strip()
        return next_line.startswith('"""') or next_line.startswith("'''")

    def _extract_function_name(self, line):
        """Extract function name from definition"""
        import re
        match = re.match(r'def\s+(\w+)\s*\(', line.strip())
        return match.group(1) if match else None

    def _extract_class_name(self, line):
        """Extract class name from definition"""
        import re
        match = re.match(r'class\s+(\w+)', line.strip())
        return match.group(1) if match else None

    def _create_function_docstring(self, func_name, func_line):
        """Create a simple function docstring"""
        import re

        # Extract parameters
        params = []
        match = re.search(r'def\s+\w+\s*\((.*?)\)', func_line)
        if match:
            params_str = match.group(1)
            for param in params_str.split(','):
                param = param.strip()
                if param and param != 'self':
                    if '=' in param:
                        param = param.split('=')[0].strip()
                    params.append(param)

        docstring = f"{func_name}."

        if params:
            docstring += f"\n\nArgs:"
            for param in params:
                docstring += f"\n    {param}: Description"

        docstring += "\n\nReturns:\n    Description of return value"

        return docstring

    def _create_class_docstring(self, class_name):
        """Create a simple class docstring"""
        return f"{class_name}.\n\nClass description."

    def _show_preview(self, original, documented):
        """Show a preview of changes"""
        original_lines = original.split('\n')
        documented_lines = documented.split('\n')

        print("\n🔍 PREVIEW OF CHANGES:")
        print("=" * 60)

        # Show first 10 lines of each for comparison
        print("ORIGINAL (first 10 lines):")
        for i, line in enumerate(original_lines[:10]):
            print(f"  {i+1:2d}: {line}")

        print("\nDOCUMENTED (first 10 lines):")
        for i, line in enumerate(documented_lines[:10]):
            print(f"  {i+1:2d}: {line}")

        print("=" * 60)
        print(f"Original: {len(original_lines)} lines")
        print(f"Documented: {len(documented_lines)} lines")
        print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description='Fixed Documentation Assistant')
    parser.add_argument('path', help='File or directory path')
    parser.add_argument('--preview', action='store_true', help='Preview changes without modifying files')

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"❌ Path does not exist: {args.path}")
        return

    # First, restore your original file if it has {code} issue
    if os.path.isfile(args.path):
        with open(args.path, 'r', encoding='utf-8') as f:
            content = f.read()

        if "{code}" in content:
            print("🔄 Found {code} issue, restoring from backup...")
            # Look for backup files
            backup_files = list(Path(os.path.dirname(args.path)).glob(f"{os.path.basename(args.path)}.backup*"))
            if backup_files:
                latest_backup = max(backup_files, key=os.path.getctime)
                with open(latest_backup, 'r', encoding='utf-8') as f:
                    backup_content = f.read()
                with open(args.path, 'w', encoding='utf-8') as f:
                    f.write(backup_content)
                print(f"✅ Restored from {latest_backup.name}")
            else:
                print("❌ No backup found, you'll need to manually fix the file")
                return

    generator = FixedDocGenerator()

    if os.path.isfile(args.path) and args.path.endswith('.py'):
        generator.generate_documentation(args.path, preview=args.preview)
    else:
        py_files = list(Path(args.path).rglob("*.py"))
        print(f"📁 Found {len(py_files)} Python files")

        for file_path in py_files:
            generator.generate_documentation(str(file_path), preview=args.preview)

if __name__ == '__main__':
    main()
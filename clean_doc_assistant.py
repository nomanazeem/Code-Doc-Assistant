#!/usr/bin/env python3
"""
Minimal Documentation Assistant

A simple tool to add documentation to Python files using either Gemini AI or local templates.
"""

import os
import argparse
from pathlib import Path
import datetime


class DocGenerator:
    """Generate documentation for Python files"""

    def __init__(self):
        """Initialize the documentation generator"""
        self.gemini_available = self._check_gemini()

    def _check_gemini(self):
        """Check if Gemini API is available"""
        try:
            import google.generativeai as genai
            from dotenv import load_dotenv
            load_dotenv()

            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-pro')
                print("✅ Gemini AI available")
                return True
            else:
                print("ℹ️  No Gemini API key found")
                return False
        except ImportError:
            print("ℹ️  google-generativeai not installed")
            return False
        except Exception as e:
            print(f"ℹ️  Gemini not available: {e}")
            return False

    def process(self, path, preview=False):
        """Process a file or directory"""
        if os.path.isfile(path) and path.endswith('.py'):
            self._process_file(path, preview)
        elif os.path.isdir(path):
            self._process_directory(path, preview)
        else:
            print(f"❌ Invalid path: {path}")

    def _process_directory(self, directory, preview):
        """Process all Python files in a directory"""
        py_files = list(Path(directory).rglob("*.py"))
        print(f"📁 Found {len(py_files)} Python files")

        for file_path in py_files:
            self._process_file(str(file_path), preview)

    def _process_file(self, file_path, preview):
        """Process a single Python file"""
        print(f"📄 Processing: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original = f.read()

            # Generate documentation
            if self.gemini_available:
                documented = self._with_gemini(original)
            else:
                documented = self._local_docs(original, file_path)

            if preview:
                self._preview(original, documented)
            else:
                self._save_file(file_path, original, documented)

        except Exception as e:
            print(f"  ❌ Error: {e}")

    def _with_gemini(self, content):
        """Use Gemini to generate documentation"""
        try:
            prompt = f"Add Python documentation to this code. Return only the documented code:\n\n{content}"
            response = self.model.generate_content(prompt)
            result = response.text.strip()

            # Clean response
            if "```python" in result:
                result = result.split("```python")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]

            return result
        except Exception as e:
            print(f"    Gemini error: {e}, using local method")
            return self._local_docs(content, "file.py")

    def _local_docs(self, content, file_path):
        """Generate documentation locally"""
        lines = content.split('\n')
        output = []

        # Add module docstring if missing
        if not any(line.strip().startswith('"""') for line in lines[:5]):
            output.append(f'"""{os.path.basename(file_path)}')
            output.append('')
            output.append('Module description.')
            output.append('"""')
            output.append('')

        # Add existing content
        output.extend(lines)

        return '\n'.join(output)

    def _preview(self, original, documented):
        """Show preview of changes"""
        print("  🔍 Preview mode - no changes saved")
        print(f"  Original: {len(original.splitlines())} lines")
        print(f"  Documented: {len(documented.splitlines())} lines")

    def _save_file(self, file_path, original, documented):
        """Save documented file with backup"""
        # Create backup
        backup_path = f"{file_path}.backup_{datetime.datetime.now().strftime('%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original)

        # Save documented version
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(documented)

        print(f"  ✅ Documentation added (backup: {os.path.basename(backup_path)})")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Minimal Documentation Assistant')
    parser.add_argument('path', help='Python file or directory to process')
    parser.add_argument('--preview', action='store_true', help='Preview changes without saving')

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"❌ Path does not exist: {args.path}")
        return

    generator = DocGenerator()
    generator.process(args.path, args.preview)


if __name__ == '__main__':
    main()
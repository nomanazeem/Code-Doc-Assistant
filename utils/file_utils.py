import os
from pathlib import Path
from typing import List

def find_python_files(directory: str) -> List[str]:
    """Find all Python files in a directory recursively"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def ensure_directory_exists(directory: str):
    """Ensure a directory exists, create if it doesn't"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def read_file_content(file_path: str) -> str:
    """Read file content with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return ""

def write_file_content(file_path: str, content: str):
    """Write content to file with error handling"""
    try:
        ensure_directory_exists(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")
        return False
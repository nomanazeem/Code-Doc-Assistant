# utils/file_utils.py
import os
from pathlib import Path
from typing import List, Optional

def read_file(file_path: str) -> str:
    """Read content from a file with proper encoding handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback to latin-1 if utf-8 fails
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()

def write_file(file_path: str, content: str) -> bool:
    """Write content to a file, creating directories if needed."""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")
        return False

def get_file_extension(file_path: str) -> str:
    """Get the file extension in lowercase."""
    return Path(file_path).suffix.lower()

def is_code_file(file_path: str, supported_extensions: List[str] = None) -> bool:
    """Check if a file is a code file based on its extension."""
    if supported_extensions is None:
        supported_extensions = [
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
            '.rs', '.go', '.rb', '.php', '.swift', '.kt', '.scala'
        ]

    extension = get_file_extension(file_path)
    return extension in supported_extensions

def normalize_path(path: str) -> str:
    """Normalize a path to absolute path."""
    return str(Path(path).resolve())

def find_code_files(directory: str, supported_extensions: List[str] = None) -> List[str]:
    """Find all code files in a directory recursively."""
    directory_path = Path(directory)
    code_files = []

    for file_path in directory_path.rglob('*'):
        if file_path.is_file() and is_code_file(str(file_path), supported_extensions):
            code_files.append(str(file_path))

    return code_files
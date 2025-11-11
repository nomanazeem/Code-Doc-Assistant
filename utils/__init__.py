# utils/__init__.py
"""
Utility functions for Code Documentation Assistant.

Contains helper functions for file operations and other utilities.
"""

from .file_utils import (
    read_file,
    write_file,
    get_file_extension,
    is_code_file,
    normalize_path
)

__all__ = [
    'read_file',
    'write_file',
    'get_file_extension',
    'is_code_file',
    'normalize_path'
]
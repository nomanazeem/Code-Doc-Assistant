# main.py
#!/usr/bin/env python3
"""
Code Documentation Assistant

A tool that helps developers generate and improve code documentation
using a multi-agent RAG pipeline.
"""

import sys
from cli.commands import cli

def main():
    """Main entry point for the Code Documentation Assistant."""
    try:
        cli()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
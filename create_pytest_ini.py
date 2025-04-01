#!/usr/bin/env python
"""
Script to create a pytest.ini file and diagnose import issues
"""
import os
import sys
from pathlib import Path

def main():
    """
    Create a pytest.ini file and print diagnostic information
    """
    # Get the current directory
    current_dir = Path.cwd()
    
    # Print diagnostic information
    print("Python path:")
    for path in sys.path:
        print(f"  {path}")
    
    print("\nCurrent directory structure:")
    for root, dirs, files in os.walk(current_dir):
        level = root.replace(str(current_dir), "").count(os.sep)
        indent = " " * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = " " * 4 * (level + 1)
        for file in files:
            if not file.startswith(".") and not "__pycache__" in root:
                print(f"{sub_indent}{file}")
    
    # Create the pytest.ini file
    pytest_ini = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Add the src directory to Python path
pythonpath = .

addopts = --verbose
"""
    
    # Write the file
    with open("pytest.ini", "w") as f:
        f.write(pytest_ini)
    
    print("\nCreated pytest.ini file with correct Python path")
    print("Now try running: uv run pytest")

if __name__ == "__main__":
    main() 
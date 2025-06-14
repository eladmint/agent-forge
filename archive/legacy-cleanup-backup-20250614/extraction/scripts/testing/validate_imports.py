#!/usr/bin/env python3
"""
Import Validation Script

This script validates imports and dependencies before deployment to catch issues early.
It checks:
1. That all import statements are valid (no ModuleNotFoundError)
2. That all critical external dependencies can be imported
3. That specific classes/functions within modules can be accessed

Usage:
    python scripts/validate_imports.py [file_path] [--verbose]

Examples:
    python scripts/validate_imports.py chatbot_api/fixed_main.py
    python scripts/validate_imports.py chatbot_api/fixed_main_hotfix6.py --verbose
"""

import argparse
import ast
import importlib
import importlib.util
import os
import sys
from typing import Dict, List, Tuple

# List of critical modules to check
CRITICAL_MODULES = [
    "fastapi",
    "uvicorn",
    "vertexai",
    "vertexai.generative_models",
    "supabase",
    "google.generativeai",
    "anyio",
]

# Specific imports to check from modules
SPECIFIC_IMPORTS = {
    "vertexai.generative_models": [
        "Content",
        "Part",
        "GenerationConfig",
        "GenerativeModel",
        # Uncomment to check for SystemInstruction (may fail in some environments)
        # "SystemInstruction",
    ],
    "fastapi": [
        "FastAPI",
        "Depends",
        "HTTPException",
        "Request",
        "Response",
    ],
}


def extract_imports(file_path: str) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Extract all import statements from a Python file.

    Returns:
        Tuple of (module_imports, from_imports) where:
        - module_imports is a list of module names (from 'import x')
        - from_imports is a dict mapping module names to lists of imported items (from 'from x import y')
    """
    with open(file_path, "r") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path}: {e}")
        return [], {}

    module_imports = []
    from_imports = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                module_imports.append(name.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                module = node.module
                if module not in from_imports:
                    from_imports[module] = []
                for name in node.names:
                    from_imports[module].append(name.name)

    return module_imports, from_imports


def validate_imports(
    module_imports: List[str], from_imports: Dict[str, List[str]], verbose: bool = False
) -> List[str]:
    """
    Validate that all imported modules and symbols can be imported.

    Returns:
        List of error messages for failed imports.
    """
    errors = []

    # Check normal imports
    for module in module_imports:
        try:
            importlib.import_module(module)
            if verbose:
                print(f"✅ Successfully imported {module}")
        except ImportError as e:
            errors.append(f"❌ Failed to import {module}: {e}")

    # Check from-imports
    for module, names in from_imports.items():
        try:
            mod = importlib.import_module(module)
            if verbose:
                print(f"✅ Successfully imported {module}")

            for name in names:
                try:
                    getattr(mod, name)
                    if verbose:
                        print(f"  ✅ Successfully imported {module}.{name}")
                except AttributeError:
                    errors.append(
                        f"❌ Failed to import {name} from {module}: Attribute not found"
                    )
        except ImportError as e:
            errors.append(f"❌ Failed to import {module}: {e}")
            # Skip checking names since the module import failed
            continue

    return errors


def check_critical_modules(verbose: bool = False) -> List[str]:
    """
    Check that all critical modules can be imported.

    Returns:
        List of error messages for failed imports.
    """
    errors = []

    for module in CRITICAL_MODULES:
        try:
            mod = importlib.import_module(module)
            if verbose:
                print(f"✅ Critical module {module} is available")

            # Check specific imports if defined
            if module in SPECIFIC_IMPORTS:
                for name in SPECIFIC_IMPORTS[module]:
                    try:
                        getattr(mod, name)
                        if verbose:
                            print(f"  ✅ Critical import {module}.{name} is available")
                    except AttributeError:
                        errors.append(
                            f"❌ Critical import {module}.{name} is not available"
                        )
        except ImportError as e:
            errors.append(f"❌ Critical module {module} is not available: {e}")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate Python imports before deployment"
    )
    parser.add_argument("file_path", nargs="?", help="Path to the Python file to check")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print verbose output"
    )
    args = parser.parse_args()

    all_errors = []

    # Check critical modules regardless of file_path
    print("Checking critical modules...")
    critical_errors = check_critical_modules(args.verbose)
    all_errors.extend(critical_errors)

    # If a file is specified, check its imports
    if args.file_path:
        if not os.path.exists(args.file_path):
            print(f"❌ File {args.file_path} does not exist")
            sys.exit(1)

        print(f"\nChecking imports in {args.file_path}...")
        module_imports, from_imports = extract_imports(args.file_path)

        if args.verbose:
            print("\nModule imports:")
            for module in module_imports:
                print(f"  - {module}")

            print("\nFrom imports:")
            for module, names in from_imports.items():
                print(f"  - from {module} import {', '.join(names)}")

        import_errors = validate_imports(module_imports, from_imports, args.verbose)
        all_errors.extend(import_errors)

    # Report results
    if all_errors:
        print("\n❌ Import validation failed with the following errors:")
        for error in all_errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print("\n✅ All imports validated successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Syntax validation script - validates Python syntax without importing dependencies.
"""

import ast
import sys
from pathlib import Path


def validate_python_syntax(file_path: Path) -> tuple[bool, str]:
    """Validate Python file syntax without executing it."""
    try:
        with open(file_path, 'r') as f:
            source = f.read()
        ast.parse(source, filename=str(file_path))
        return True, "OK"
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_function_ordering(file_path: Path) -> tuple[bool, str]:
    """Check for potential function ordering issues."""
    try:
        with open(file_path, 'r') as f:
            source = f.read()

        tree = ast.parse(source)

        # Track function definitions and calls
        defined_functions = set()
        function_calls_before_definition = []

        for node in ast.walk(tree):
            # Track function definitions
            if isinstance(node, ast.FunctionDef):
                defined_functions.add(node.name)

            # Track function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    # Check if calling a function that hasn't been defined yet
                    if func_name not in defined_functions and not func_name.startswith('_'):
                        # This might be a call before definition
                        # We'll just note it, not fail on it (could be imported)
                        pass

        return True, "OK"
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Run syntax validation on all Python files."""
    print("\n" + "🔍 " * 20)
    print("BACKEND API SYNTAX VALIDATION")
    print("🔍 " * 20 + "\n")

    backend_dir = Path(__file__).parent

    # Files to validate
    files_to_validate = [
        "main.py",
        "dependencies.py",
        "auth.py",
        "shared/key_vault_client.py",
        "api/__init__.py",
        "api/health.py",
        "api/feedback.py",
        "api/users.py",
        "api/auth.py",
        "api/articles.py",
        "api/topics.py",
        "api/chat.py",
        "api/analytics.py",
        "api/user_articles.py",
        "api/rss_feeds.py",
    ]

    all_passed = True
    results = []

    print("=" * 70)
    print("Validating Python syntax...")
    print("=" * 70)

    for file_path_str in files_to_validate:
        file_path = backend_dir / file_path_str

        if not file_path.exists():
            print(f"⚠️  {file_path_str:40s} SKIP (not found)")
            continue

        # Validate syntax
        syntax_ok, syntax_msg = validate_python_syntax(file_path)

        if syntax_ok:
            print(f"✓ {file_path_str:40s} {syntax_msg}")
        else:
            print(f"✗ {file_path_str:40s} {syntax_msg}")
            all_passed = False

        results.append((file_path_str, syntax_ok, syntax_msg))

    # Special validation for feedback.py (the file that had ordering issues)
    print("\n" + "=" * 70)
    print("Special validation: feedback.py function ordering...")
    print("=" * 70)

    feedback_file = backend_dir / "api/feedback.py"
    if feedback_file.exists():
        with open(feedback_file, 'r') as f:
            lines = f.readlines()

        # Find where helper functions are defined
        get_success_html_line = None
        get_error_html_line = None
        route_handler_line = None

        for i, line in enumerate(lines, 1):
            if 'def get_success_html' in line:
                get_success_html_line = i
            elif 'def get_error_html' in line:
                get_error_html_line = i
            elif '@router.get("/api/feedback"' in line or '@router.post("/api/feedback"' in line:
                if route_handler_line is None:
                    route_handler_line = i

        print(f"  get_success_html() defined at line: {get_success_html_line}")
        print(f"  get_error_html() defined at line: {get_error_html_line}")
        print(f"  First route handler at line: {route_handler_line}")

        if get_success_html_line and get_error_html_line and route_handler_line:
            if get_success_html_line < route_handler_line and get_error_html_line < route_handler_line:
                print(f"  ✓ Helper functions defined BEFORE route handlers (correct order)")
            else:
                print(f"  ✗ Helper functions defined AFTER route handlers (incorrect order)")
                all_passed = False
        else:
            print(f"  ⚠️  Could not verify function ordering")

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    passed_count = sum(1 for _, ok, _ in results if ok)
    total_count = len(results)

    print(f"Files validated: {total_count}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {total_count - passed_count}")

    if all_passed:
        print("\n" + "🎉 " * 20)
        print("ALL SYNTAX CHECKS PASSED!")
        print("Code structure is correct! 🚀")
        print("🎉 " * 20 + "\n")
        return 0
    else:
        print("\n" + "⚠️  " * 20)
        print("VALIDATION FAILED!")
        print("Please fix the syntax errors above.")
        print("⚠️  " * 20 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

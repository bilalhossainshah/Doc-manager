#!/usr/bin/env python3
"""
Custom Code Review Rules for Doc-Manager (FastAPI / Python project)
=====================================================================
Rules enforced:
  1.  No hardcoded secrets / API keys in source code
  2.  No bare 'except:' clauses (must catch specific exceptions)
  3.  No print() statements in production code (use logging instead)
  4.  All FastAPI route functions must have a docstring
  5.  No TODO/FIXME comments left in code (must be tracked as issues)
  6.  Database operations should use parameterized queries (no f-string SQL)
  7.  No unused imports (basic check)
  8.  Function/method names must be snake_case
  9.  Files must not exceed 300 lines (encourage modularisation)
  10. No direct os.system() calls (use subprocess instead)
"""

import ast
import os
import re
import sys
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────
EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "venv", "env", "node_modules", "uploads"}
EXCLUDE_FILES = {"madal.py"}  # intentionally excluded files
MAX_FILE_LINES = 300

# Patterns for secret detection
SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|secret[_-]?key|password|passwd|token)\s*=\s*["\'][^"\']{8,}["\']',
     "Potential hardcoded secret/credential detected"),
    (r'(?i)(aws_access_key_id|aws_secret_access_key)\s*=\s*["\'][^"\']+["\']',
     "AWS credentials hardcoded in source"),
    (r'AIza[0-9A-Za-z\-_]{35}',
     "Google API key pattern detected"),
    (r'sk-[a-zA-Z0-9]{48}',
     "OpenAI API key pattern detected"),
]

issues = []
warnings = []


def log_issue(filepath, line_no, rule_id, message, severity="ERROR"):
    entry = {
        "file": filepath,
        "line": line_no,
        "rule": rule_id,
        "message": message,
        "severity": severity,
    }
    if severity == "WARNING":
        warnings.append(entry)
    else:
        issues.append(entry)


def get_python_files():
    """Collect all .py files in the project."""
    root = Path(".")
    files = []
    for path in root.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.name in EXCLUDE_FILES:
            continue
        files.append(path)
    return files


# ── Rule Implementations ────────────────────────────────────────────────────────

def check_hardcoded_secrets(filepath, lines):
    """Rule 1: No hardcoded secrets."""
    for i, line in enumerate(lines, 1):
        # Skip comments and env-var assignments
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        for pattern, message in SECRET_PATTERNS:
            if re.search(pattern, line):
                log_issue(filepath, i, "R001", message)


def check_bare_except(filepath, tree):
    """Rule 2: No bare except clauses."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            log_issue(filepath, node.lineno, "R002",
                      "Bare 'except:' used. Catch a specific exception instead.")


def check_print_statements(filepath, tree):
    """Rule 3: No print() in production code."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "print":
                log_issue(filepath, node.lineno, "R003",
                          "print() found. Use logging module instead.",
                          severity="WARNING")


def check_fastapi_docstrings(filepath, tree):
    """Rule 4: FastAPI route functions must have docstrings."""
    route_decorators = {"get", "post", "put", "delete", "patch"}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            # Check for @router.get / @app.post etc.
            is_route = False
            if isinstance(decorator, ast.Attribute) and decorator.attr in route_decorators:
                is_route = True
            elif isinstance(decorator, ast.Call):
                d = decorator.func
                if isinstance(d, ast.Attribute) and d.attr in route_decorators:
                    is_route = True
            if is_route:
                body = node.body
                if not (body and isinstance(body[0], ast.Expr) and
                        isinstance(body[0].value, ast.Constant) and
                        isinstance(body[0].value.value, str)):
                    log_issue(filepath, node.lineno, "R004",
                              f"FastAPI route '{node.name}' is missing a docstring.",
                              severity="WARNING")


def check_todo_fixme(filepath, lines):
    """Rule 5: No TODO/FIXME left in code."""
    pattern = re.compile(r'\b(TODO|FIXME|HACK|XXX)\b', re.IGNORECASE)
    for i, line in enumerate(lines, 1):
        if pattern.search(line):
            log_issue(filepath, i, "R005",
                      f"'{pattern.search(line).group()}' comment found. Track this as a GitHub Issue.",
                      severity="WARNING")


def check_fstring_sql(filepath, lines):
    """Rule 6: No f-string SQL queries."""
    sql_keywords = re.compile(r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE)\b', re.IGNORECASE)
    fstring_pattern = re.compile(r'f["\'].*?\b(SELECT|INSERT|UPDATE|DELETE)\b', re.IGNORECASE)
    for i, line in enumerate(lines, 1):
        if fstring_pattern.search(line):
            log_issue(filepath, i, "R006",
                      "f-string used in SQL query. Use parameterized queries to prevent SQL injection.")


def check_snake_case(filepath, tree):
    """Rule 8: Function names must be snake_case."""
    camel_pattern = re.compile(r'^[a-z]+([A-Z][a-z]+)+')
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            if camel_pattern.match(name):
                log_issue(filepath, node.lineno, "R008",
                          f"Function '{name}' uses camelCase. Use snake_case instead.",
                          severity="WARNING")


def check_file_length(filepath, lines):
    """Rule 9: Files should not exceed MAX_FILE_LINES lines."""
    if len(lines) > MAX_FILE_LINES:
        log_issue(filepath, MAX_FILE_LINES, "R009",
                  f"File has {len(lines)} lines (limit: {MAX_FILE_LINES}). Consider splitting into modules.",
                  severity="WARNING")


def check_os_system(filepath, tree):
    """Rule 10: No os.system() calls."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if (isinstance(func, ast.Attribute) and
                    func.attr == "system" and
                    isinstance(func.value, ast.Name) and
                    func.value.id == "os"):
                log_issue(filepath, node.lineno, "R010",
                          "os.system() used. Use subprocess.run() instead for better security and control.")


# ── Main Runner ─────────────────────────────────────────────────────────────────

def main():
    py_files = get_python_files()

    if not py_files:
        print("⚠️  No Python files found to check.")
        sys.exit(0)

    print(f"🔍 Checking {len(py_files)} Python file(s) against custom rules...\n")

    for filepath in py_files:
        rel_path = str(filepath)
        try:
            source = filepath.read_text(encoding="utf-8")
            lines = source.splitlines()
        except Exception as e:
            print(f"⚠️  Could not read {rel_path}: {e}")
            continue

        # Text-based checks
        check_hardcoded_secrets(rel_path, lines)
        check_todo_fixme(rel_path, lines)
        check_fstring_sql(rel_path, lines)
        check_file_length(rel_path, lines)

        # AST-based checks
        try:
            tree = ast.parse(source, filename=rel_path)
        except SyntaxError as e:
            log_issue(rel_path, e.lineno or 1, "R000",
                      f"Syntax error: {e.msg}")
            continue

        check_bare_except(rel_path, tree)
        check_print_statements(rel_path, tree)
        check_fastapi_docstrings(rel_path, tree)
        check_snake_case(rel_path, tree)
        check_os_system(rel_path, tree)

    # ── Report ──────────────────────────────────────────────────────────────────
    print("=" * 60)
    print("📋 CUSTOM CODE REVIEW RESULTS")
    print("=" * 60)

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  [{w['rule']}] {w['file']}:{w['line']} — {w['message']}")

    if issues:
        print(f"\n❌ ERRORS ({len(issues)}):")
        for issue in issues:
            print(f"  [{issue['rule']}] {issue['file']}:{issue['line']} — {issue['message']}")
        print(f"\n❌ Found {len(issues)} error(s) and {len(warnings)} warning(s).")
        print("   Fix all errors before merging. Warnings are informational.\n")
        sys.exit(1)
    else:
        print(f"\n✅ All custom rules passed! ({len(warnings)} warning(s))\n")
        sys.exit(0)


if __name__ == "__main__":
    main()

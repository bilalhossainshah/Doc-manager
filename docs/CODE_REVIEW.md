# 🤖 Automated Code Review Pipeline — Doc-Manager

> **Repository:** [bilalhossainshah/Doc-manager](https://github.com/bilalhossainshah/Doc-manager)  
> **Stack:** Python 3.11 · FastAPI · GitHub Actions  
> **Cost:** 100% Free (all open-source tools)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [File Structure](#file-structure)
4. [Pipeline Jobs](#pipeline-jobs)
5. [Custom Rules Reference](#custom-rules-reference)
6. [How to Trigger a Review](#how-to-trigger-a-review)
7. [Reading the Results](#reading-the-results)
8. [How to Add or Modify Rules](#how-to-add-or-modify-rules)
9. [Blocking Merges Until Checks Pass](#blocking-merges-until-checks-pass)
10. [Tools Used](#tools-used)
11. [Troubleshooting](#troubleshooting)

---

## Overview

This pipeline **automatically reviews every Pull Request** before it can be merged into `main`. It enforces code quality, formatting standards, security best practices, and project-specific custom rules — **without any manual review needed for routine issues**.

### What happens on every PR:

```
Developer opens Pull Request
           │
           ▼
  ┌─────────────────────┐
  │  GitHub Actions      │  ← Triggers automatically
  │  runs 5 parallel     │
  │  jobs               │
  └─────────────────────┘
           │
     ┌─────┴──────┐
     │            │
     ▼            ▼
Inline comments   Summary comment
on specific       posted on the PR
lines of code     conversation
```

---

## How It Works

The workflow is defined in `.github/workflows/code-review.yml`.

### Trigger Conditions

```yaml
on:
  pull_request:
    branches: [main, master, develop]
    types: [opened, synchronize, reopened]
```

| Event | Description |
|-------|-------------|
| `opened` | A new PR is created |
| `synchronize` | New commits are pushed to an existing PR |
| `reopened` | A closed PR is reopened |

The review runs on **every push to a PR** — so if you fix something and push again, the review re-runs automatically.

---

## File Structure

```
Doc-manager/
├── .github/
│   ├── workflows/
│   │   └── code-review.yml          ← Main CI pipeline (5 jobs)
│   └── scripts/
│       └── custom_rules_check.py    ← Custom rule checker (10 rules)
├── docs/
│   └── CODE_REVIEW.md               ← This file
└── ruff.toml                        ← Ruff linter configuration
```

---

## Pipeline Jobs

The pipeline runs **5 jobs in parallel**, then a final summary:

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ 🎨 Formatting    │  │ 🔎 Linting       │  │ 🔒 Security      │  │ 📋 Custom Rules  │
│ (Black + isort)  │  │ (Ruff)           │  │ (Bandit)         │  │ (10 rules)       │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                      │                      │
         └─────────────────────┴──────────────────────┴──────────────────────┘
                                          │
                                          ▼
                               ┌──────────────────────┐
                               │ 📊 Review Summary    │
                               │ (bot PR comment)     │
                               └──────────────────────┘
```

---

### Job 1 — 🎨 Formatting Check (Black + isort)

**Tool:** [Black](https://github.com/psf/black) + [isort](https://github.com/PyCQA/isort) + [Reviewdog](https://github.com/reviewdog/reviewdog)

**What it checks:**
- Code is formatted according to **Black** style (consistent indentation, quotes, line breaks)
- Imports are sorted in the correct order with **isort**

**Output:** Reviewdog posts **inline comments on the PR** on each line that needs reformatting.

**How to fix locally:**
```bash
pip install black isort
black .           # auto-fix formatting
isort .           # auto-fix import order
```

---

### Job 2 — 🔎 Linting (Ruff)

**Tool:** [Ruff](https://github.com/astral-sh/ruff) + [Reviewdog](https://github.com/reviewdog/reviewdog)

**What it checks** (rule categories enabled in `ruff.toml`):

| Code | Category | Example |
|------|----------|---------|
| `E/W` | pycodestyle | Whitespace, indentation errors |
| `F` | Pyflakes | Unused imports, undefined names |
| `I` | isort | Import order |
| `N` | pep8-naming | Class/function naming conventions |
| `UP` | pyupgrade | Old Python syntax (use f-strings, etc.) |
| `B` | flake8-bugbear | Likely bugs (mutable defaults, etc.) |
| `A` | flake8-builtins | Shadowing built-in names |
| `C4` | flake8-comprehensions | Simplify list/dict comprehensions |
| `SIM` | flake8-simplify | Simplifiable code patterns |

**Output:** Inline PR comments on each flagged line.

**How to fix locally:**
```bash
pip install ruff
ruff check .          # show all issues
ruff check --fix .    # auto-fix what's possible
```

---

### Job 3 — 🔒 Security Scan (Bandit)

**Tool:** [Bandit](https://github.com/PyCQA/bandit) + [Reviewdog](https://github.com/reviewdog/reviewdog)

**What it checks:**
- Hardcoded passwords or secrets
- Use of `eval()` or `exec()`
- Insecure use of `subprocess` with `shell=True`
- SQL injection patterns
- Insecure random number generation
- Use of weak cryptographic algorithms (MD5, SHA1)
- Insecure deserialization

> **Note:** `B101` (assert statements) is skipped as it's common in test files.

**Output:** Inline PR comments on each security issue found.

**Severity levels:**

| Level | Meaning |
|-------|---------|
| `LOW` | Informational — review but may be acceptable |
| `MEDIUM` | Should be addressed before merge |
| `HIGH` | Must be fixed — blocks merge if protection rules are enabled |

---

### Job 4 — 📋 Custom Rules Check

**Tool:** Custom Python script — `.github/scripts/custom_rules_check.py`

This is a **project-specific rule engine** tailored to the Doc-Manager codebase.

**How it works:**
1. Scans all `.py` files in the project (excluding `.venv`, `uploads`, etc.)
2. Runs **text-based checks** (regex on raw source)
3. Runs **AST-based checks** (parses Python syntax tree for deeper analysis)
4. Reports `ERRORS` (blocking) and `WARNINGS` (informational)

See the [Custom Rules Reference](#custom-rules-reference) section for full details.

---

### Job 5 — 📊 Review Summary

**Tool:** [actions/github-script](https://github.com/actions/github-script)

Runs **after all other jobs complete** and posts a summary table as a comment on the PR:

```
## 🤖 Automated Code Review Report

| Check                         | Status     |
|-------------------------------|------------|
| 🎨 Formatting (Black + isort) | ✅ success |
| 🔎 Linting (Ruff)             | ✅ success |
| 🔒 Security (Bandit)          | ✅ success |
| 📋 Custom Rules               | ✅ success |
```

> **Smart deduplication:** If the PR already has a summary comment from a previous run, it **updates** the existing comment instead of creating a new one.

---

## Custom Rules Reference

All rules are defined in `.github/scripts/custom_rules_check.py`:

| Rule ID | Severity | What It Catches | Detection Method |
|---------|----------|-----------------|-----------------|
| `R001` | ❌ ERROR | Hardcoded API keys, passwords, tokens | Regex |
| `R002` | ❌ ERROR | Bare `except:` clauses | AST |
| `R003` | ⚠️ WARNING | `print()` instead of `logging` | AST |
| `R004` | ⚠️ WARNING | FastAPI routes missing docstrings | AST |
| `R005` | ⚠️ WARNING | `TODO` / `FIXME` / `HACK` comments | Regex |
| `R006` | ❌ ERROR | f-string SQL queries (SQL injection risk) | Regex |
| `R008` | ⚠️ WARNING | camelCase function names (use snake_case) | AST |
| `R009` | ⚠️ WARNING | Files exceeding 300 lines | Line count |
| `R010` | ❌ ERROR | `os.system()` calls (use `subprocess` instead) | AST |

> **Severity guide:**
> - **ERROR** — Fails the check job. Blocks merge if branch protection is enabled.
> - **WARNING** — Informational only. Check still passes.

### Secret Detection Patterns (R001)

The following credential patterns are detected:

```python
# General secrets (any assignment with 8+ char value)
api_key = "..."
secret_key = "..."
password = "..."
token = "..."

# AWS credentials
aws_access_key_id = "..."
aws_secret_access_key = "..."

# Google API keys  (pattern: AIza + 35 chars)
AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# OpenAI API keys  (pattern: sk- + 48 chars)
sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Safe pattern** — use environment variables instead:
```python
import os
api_key = os.getenv("API_KEY")  # ✅ this will NOT trigger R001
```

---

## How to Trigger a Review

### Automatic (recommended)

Simply open a Pull Request on GitHub. The review starts **automatically within seconds**.

```bash
# 1. Create a feature branch
git checkout -b feature/your-feature-name

# 2. Make your changes, then commit
git add .
git commit -m "feat: describe your changes"

# 3. Push the branch
git push origin feature/your-feature-name

# 4. Open a PR on GitHub
#    → Go to: https://github.com/bilalhossainshah/Doc-manager
#    → Click "Compare & pull request"
#    → Click "Create pull request"
#    ✅ Review starts automatically!
```

### Manual (run locally before pushing)

Run each tool locally to catch issues before opening a PR:

```bash
# Install all tools (one time)
pip install black isort ruff bandit

# Check formatting
black --check .
isort --check-only .

# Check linting
ruff check .

# Check security
bandit -r . --skip B101

# Check custom rules
python3 .github/scripts/custom_rules_check.py
```

### Auto-fix common issues locally

```bash
# Auto-fix formatting
black .
isort .

# Auto-fix linting (where possible)
ruff check --fix .
```

---

## Reading the Results

### Where to find results on GitHub

| Location | What you'll find |
|----------|-----------------|
| PR → **Checks tab** | All 5 jobs with ✅/❌ status and live logs |
| PR → **Files changed tab** | Inline Reviewdog comments on specific lines |
| PR → **Conversation tab** (scroll down) | Bot summary table comment |
| **Actions tab** | Full history of all pipeline runs |

### Understanding inline comments

Reviewdog posts comments directly on the diff in **Files changed**:

```
📍 retrieval.py, line 89
────────────────────────────────────────
Ruff Linter [F401]: `json` imported but unused
```

```
📍 routers/upload.py, line 17
────────────────────────────────────────
Black Formatter: would reformat — indentation does not match expected
```

### Understanding the Actions log

Go to **Actions → latest run → click a job** to see detailed output:

```
🔍 Checking 11 Python file(s) against custom rules...

============================================================
📋 CUSTOM CODE REVIEW RESULTS
============================================================

⚠️  WARNINGS (3):
  [R003] main.py:24 — print() found. Use logging module instead.
  [R004] routers/query.py:8 — FastAPI route 'query_documents' is missing a docstring.
  [R005] retrieval.py:45 — 'TODO' comment found. Track this as a GitHub Issue.

✅ All custom rules passed! (3 warning(s))
```

---

## How to Add or Modify Rules

### Add a new custom rule

Open `.github/scripts/custom_rules_check.py` and:

**Step 1 — Write the check function:**

```python
def check_my_new_rule(filepath, tree):
    """Rule 11: No use of deprecated function X."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "deprecated_func":
                log_issue(filepath, node.lineno, "R011",
                          "deprecated_func() is deprecated. Use new_func() instead.",
                          severity="WARNING")  # or "ERROR" to block merge
```

**Step 2 — Register it in `main()`:**

```python
# Inside the "for filepath in py_files" loop, add:
check_my_new_rule(rel_path, tree)
```

### Change rule severity (WARNING ↔ ERROR)

```python
# Make it non-blocking (warning)
log_issue(filepath, node.lineno, "R003", "message", severity="WARNING")

# Make it blocking (error)
log_issue(filepath, node.lineno, "R003", "message", severity="ERROR")
```

### Exclude specific files

```python
# At the top of custom_rules_check.py:
EXCLUDE_FILES = {"madal.py", "legacy_module.py"}
```

### Exclude a directory

```python
EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "venv", "env",
                "node_modules", "uploads", "migrations"}
```

### Change max file length

```python
MAX_FILE_LINES = 500  # default: 300
```

### Add/remove Ruff rule categories

Edit `ruff.toml` in the project root:

```toml
[lint]
# Add or remove rule category codes:
select = ["E", "W", "F", "I", "N", "UP", "B", "A", "C4", "SIM"]
ignore = ["E501", "B008"]
```

Browse all available Ruff rules: https://docs.astral.sh/ruff/rules/

---

## Blocking Merges Until Checks Pass

Currently the pipeline reports issues but **does not block merges** by default. To enforce it:

1. Go to: **GitHub → Repository Settings → Branches**
2. Click **"Add branch protection rule"**
3. Branch name pattern: `main`
4. Enable: ✅ **"Require status checks to pass before merging"**
5. Search and add these required checks:
   - `🎨 Formatting Check`
   - `🔎 Linting (Ruff)`
   - `🔒 Security Scan (Bandit)`
   - `📋 Custom Rules Check`
6. Enable: ✅ **"Require branches to be up to date before merging"**
7. Click **"Save changes"**

> ✅ After this, GitHub will **prevent merging** any PR until all 4 checks pass.

---

## Tools Used

| Tool | Purpose | License |
|------|---------|---------|
| [GitHub Actions](https://github.com/features/actions) | CI/CD runner — free for public repos, 2000 min/month for private | Free |
| [Reviewdog](https://github.com/reviewdog/reviewdog) | Posts inline PR review comments from any linter | MIT |
| [Black](https://github.com/psf/black) | Opinionated Python code formatter | MIT |
| [isort](https://github.com/PyCQA/isort) | Python import sorter | MIT |
| [Ruff](https://github.com/astral-sh/ruff) | Extremely fast Python linter (10–100x faster than flake8) | MIT |
| [Bandit](https://github.com/PyCQA/bandit) | Python security vulnerability scanner | Apache 2.0 |
| [actions/checkout@v4](https://github.com/actions/checkout) | Checks out repository code in CI | MIT |
| [actions/setup-python@v5](https://github.com/actions/setup-python) | Sets up Python environment in CI | MIT |
| [actions/github-script@v7](https://github.com/actions/github-script) | Runs GitHub API calls in CI | MIT |

**Total cost: $0** — All tools are free and open source.

---

## Troubleshooting

### ❓ The workflow isn't triggering on my PR

**Check:** Is the PR targeting `main`, `master`, or `develop`?

```yaml
# code-review.yml — update this list if needed:
branches: [main, master, develop, your-branch-name]
```

---

### ❓ "Permission denied" error in Actions logs

**Fix:** Go to **Repo Settings → Actions → General → Workflow permissions**  
Set to: **"Read and write permissions"** ✅  
Enable: **"Allow GitHub Actions to create and approve pull requests"** ✅

---

### ❓ Reviewdog isn't posting inline comments

This can happen on PRs from **forked repositories** — GitHub restricts write access from fork PRs for security reasons. It works correctly for branches within the same repo.

---

### ❓ A custom rule is flagging something it shouldn't (false positive)

Option 1 — Exclude the specific file:
```python
EXCLUDE_FILES = {"madal.py", "the_false_positive_file.py"}
```

Option 2 — Add an inline suppression comment:
```python
password = get_password()  # noqa: R001 — not a hardcoded secret, loaded at runtime
```

---

### ❓ Bandit is flagging a known acceptable pattern

Add `# nosec` with the Bandit rule ID on that line:
```python
subprocess.run(cmd, shell=True)  # nosec B602 — input is sanitized upstream
```

---

### ❓ How do I run all checks at once locally?

```bash
cd /home/bilal/Documents/Doc-manager

pip install black isort ruff bandit

echo "--- Formatting ---"
black --check .
isort --check-only .

echo "--- Linting ---"
ruff check .

echo "--- Security ---"
bandit -r . --skip B101

echo "--- Custom Rules ---"
python3 .github/scripts/custom_rules_check.py
```

---

*Documentation version: 2.0*  
*Last updated: 2026-07-15*  
*Pipeline: Reviewdog + Ruff + Black + Bandit + Custom Rules (10 rules)*

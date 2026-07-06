# Development Setup

This document explains how to set up `yini-test-suite` locally, run its checks,
and run the shared case corpus against parser adapters.

`yini-test-suite` is packaged as Python primarily so it can provide the
`yini-test-suite` command. The internal Python package is named `yini_test`, but
it is not currently intended as a stable public Python library API for other
projects to import directly.

## Prerequisites

Required:
- Python 3.10 or newer.
- `pip`.

Recommended:
- Task, for running the commands in `Taskfile.yml`.
- A virtual environment for local development.

Optional:
- A sibling `yini-parser-typescript` repository if you want to run the
  TypeScript parser adapter.
- A sibling `yini-parser-python` repository if you want to run the Python parser
  adapter.

## Install Task

On Windows:

```powershell
winget install Task.Task
```

Verify that Task is available:

```bash
task --list
```

## Verify Python

Check Python:

```bash
python --version
```

Check pip:

```bash
python -m pip --version
```

If pip is missing, try:

```bash
python -m ensurepip --upgrade
```

## Optional Virtual Environment

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate it in Command Prompt:

```bat
.\.venv\Scripts\activate.bat
```

## Install The Project

From the repository root:

```bash
task install
```

This installs development dependencies and installs `yini-test-suite` in
editable mode.

The direct commands are:

```bash
python -m pip install -r requirements-dev.txt
python -m pip install -e .
```

Editable mode is useful during development because the installed
`yini-test-suite` command uses the current working tree.

## Run The CLI

After installation, check the CLI:

```bash
yini-test-suite --help
```

You can also run the package module directly:

```bash
python -m yini_test --help
```

When running without editable installation, set `PYTHONPATH=src` first or use
the Taskfile commands, which already set it where needed.

## Project Layout

Important paths:
- `src/yini_test/cli.py` handles command-line arguments.
- `src/yini_test/runner.py` executes discovered cases and prints results.
- `src/yini_test/discovery.py` discovers valid, warning, and invalid cases.
- `src/yini_test/adapters.py` runs adapter commands and parses adapter output.
- `src/yini_test/expectations.py` loads expected JSON and warning files.
- `src/yini_test/cases/smoke/` contains quick confidence cases.
- `src/yini_test/cases/golden/` contains broader conformance cases.
- `src/yini_test/cases/manifest.json` declares the targeted YINI spec revision.
- `tests/` contains tests for the test-suite runner itself.
- `docs/` contains maintainer, adapter, runner, and case-contract documentation.
- `Taskfile.yml` contains the standard local commands.

## Common Checks

Run tests:

```bash
task test
```

Run linting:

```bash
task lint
```

Run type checking:

```bash
task typecheck
```

Check formatting:

```bash
task format-check
```

Run all project checks:

```bash
task check
```

Build the package:

```bash
task build
```

Check built package metadata:

```bash
task package-check
```

Direct equivalents:

```bash
python -m pytest -v -W error
python -m ruff check src tests
python -m ruff format --check src tests
cmd /c "set MYPYPATH=src&& python -m mypy -p yini_test --explicit-package-bases --ignore-missing-imports"
python -m build
python -m twine check dist/*
```

On Windows, the Taskfile sets `MYPYPATH=src` for mypy through `cmd /c`.

## Running Parser Adapters

The predefined adapter tasks assume this sibling layout:

```text
YINI-lang-WORK/
  yini-test-suite/
  yini-parser-typescript/
  yini-parser-python/
```

Run TypeScript parser cases:

```bash
task run-smoke-typescript-lenient
task run-smoke-typescript-strict
task run-all-typescript
```

Run Python parser cases:

```bash
task run-smoke-python-lenient
task run-smoke-python-strict
task run-all-python
```

Run all configured adapters:

```bash
task adapters-smoke
task adapters-all
```

The TypeScript tasks expect the built adapter at:

```text
../yini-parser-typescript/dist-tools/tools/yini-test-adapter.js
```

The Python tasks expect the adapter at:

```text
../yini-parser-python/tools/yini_parser_adapter.py
```

Adapters are maintained by their parser repositories. This repository only
defines and runs the shared adapter contract.

## Runner Output

The default runner output prints `PASS`, `FAIL`, and the final summary. Add
`--show-progress` to a direct `python -m yini_test ...` or `yini-test-suite ...`
command when you also want a `RUN` line before each case.

The summary identifies the test-suite version, adapter, parser package version
when it can be detected, YINI spec revision, and selected suite:

```text
YINI Test Suite Summary
yini-test-suite: 0.3.0b1
Adapter: yini-parser-typescript
Parser version: 1.6.1
YINI spec: 1.0.0 RC 6
Test suite: "all"
```

## Useful Environment Variables

`PYTHONPATH=src` lets direct module commands use the local source tree without
editable installation.

`PYTHONIOENCODING=utf-8` helps Windows terminals preserve Unicode output when
running the Python parser adapter.

`MYPYPATH=src` lets mypy find the package when running type checks directly.

## Troubleshooting

If `yini-test-suite` is not recognized as a command, run `task install` or
`python -m pip install -e .` from the repository root.

If `python -m yini_test` cannot find the package, install editable mode or set
`PYTHONPATH=src`.

If a TypeScript adapter run fails before cases execute, make sure the sibling
TypeScript parser repository has built its adapter output.

If a Python adapter run has Unicode output problems on Windows, use the Taskfile
commands or set `PYTHONIOENCODING=utf-8`.

If a parser version is shown as `unknown`, check that the adapter path is inside
a parser repository with recognizable package metadata such as `package.json`
or `pyproject.toml`.

If `format-check` reports unrelated formatting drift, keep your current change
focused and report the existing drift separately unless the task is specifically
to format the repository.

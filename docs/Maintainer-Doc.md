# Maintainer Documentation

This document describes the maintainer workflow for `yini-test-suite`.

`yini-test-suite` is the shared test harness and case corpus for YINI parser
implementations. It does not contain a YINI parser. Parser-specific adapters
live in the parser repositories, and this repository calls those adapters to
check parser behavior against the shared cases.

The Python package name is:

```text
yini-test-suite
```

The console script is:

```text
yini-test-suite
```

This project is packaged as Python primarily so it can provide the
`yini-test-suite` CLI command. The internal Python package is named `yini_test`,
but it is not currently intended as a stable public Python library API for other
projects to import directly.

For local installation, checks, adapter runs, and troubleshooting, see
`docs/Development-Setup.md`.

## Maintainer Responsibilities

Maintain this repository as the shared contract for parser implementations:
- Keep the runner behavior deterministic and implementation-agnostic.
- Keep the smoke and golden case corpus aligned with the current YINI spec.
- Keep valid, warning, and invalid case expectations consistent with the case contract.
- Keep adapter-facing behavior documented in `docs/adapter-contract.md`.
- Keep runner behavior documented in `README.md` and `docs/runner-flow.md`.
- Keep setup instructions documented in `docs/Development-Setup.md`.
- Record user-visible changes in `CHANGELOG.md`.

Parser repositories are responsible for their own parser code and adapter code.
This repository should not add parser-specific logic beyond the generic adapter
command contract.

## Case Corpus Rules

Case directories define both parser mode and expected result:
- `lenient/` cases run in lenient mode.
- `strict/` cases run in strict mode.
- `valid/` cases must parse successfully.
- `warning/` cases must parse successfully and emit expected warnings.
- `invalid/` cases must fail.

Valid cases must include:
- One `.yini` input file.
- One matching `.json` expected-output file with the same base name.

Warning cases must include:
- One `.yini` input file.
- One matching `.json` expected-output file.
- One matching `.warning.json` expected-warning file.

Invalid cases must include:
- One `.yini` input file.

Do not add `.json` sidecars for invalid cases unless the runner contract is
changed. Strict cases may use `.strict.yini` and `.strict.json` filenames, but
parser mode is determined by the directory and CLI flag, not by the filename.

Expected JSON files should be valid machine-readable JSON and should be
pretty-formatted with 4-space indentation where practical. The runner compares
parsed JSON values, so whitespace differences do not affect matching.

Expected warning files contain a JSON array. Each entry should include a
`contains` string that must appear in adapter `stderr`:

```json
[
    {
        "contains": "duplicate key"
    }
]
```

## Adding Or Changing Cases

Use this workflow for case-corpus changes:

1. Inspect nearby cases before adding new ones.
2. Add small, focused cases with descriptive lowercase hyphenated names.
3. Keep lenient and strict cases separated.
4. Add expected `.json` or `.warning.json` files according to the case contract.
5. Run `python -m pytest -v -W error`.
6. Run the relevant parser adapter tasks if the sibling parser repositories are available.
7. If a parser fails a valid corpus case, decide whether the corpus or the parser is wrong before changing expectations.

This repository defines the shared expectation. Do not relax a golden case just
to match one parser unless the YINI spec or case contract says the parser is
correct.

## Runner And CLI Changes

When changing runner or CLI behavior:
- Add or update focused tests in `tests/`.
- Update `README.md` when command-line usage or visible output changes.
- Update `docs/runner-flow.md` when execution flow changes.
- Update `docs/adapter-contract.md` when adapter-facing behavior changes.
- Update `docs/Development-Setup.md` when setup, checks, or local command usage changes.
- Keep adapter output requirements stable unless the change is intentional.

The adapter contract is intentionally small: adapters receive an input path and
mode, write exactly one JSON document to `stdout` on success, write diagnostics
to `stderr`, and use exit codes to signal success or failure.

## Verification Policy

For documentation-only changes, run:

```bash
python -m pytest -v -W error
```

For runner, discovery, expectation, adapter, or CLI changes, run the relevant
checks from `docs/Development-Setup.md`.

For case-corpus changes, also run the relevant adapter tasks when the sibling
parser repositories are available. If a required adapter cannot be run, mention
that in the handoff.

## Versioning

Keep the project version synchronized in:
- `pyproject.toml`
- `src/yini_test/__init__.py`
- tests that assert the displayed version, if any
- `CHANGELOG.md`

Use Python-compatible versions:

```text
0.3.0a1
0.3.0b1
0.3.0rc1
0.3.0
```

The current package classifier is beta:

```toml
"Development Status :: 4 - Beta"
```

Update classifiers when the release maturity changes.

## Release Preparation

Before preparing a release:
- Confirm `CHANGELOG.md` describes the release.
- Confirm `pyproject.toml` metadata and classifiers are correct.
- Confirm `src/yini_test/cases/manifest.json` targets the intended YINI spec revision.
- Run `task check`.
- Run `task build`.
- Run `task package-check`.
- Run `task run-all-typescript` and `task run-all-python` when the sibling parser repositories are available. These tasks cover the official ecosystem parser adapters, but parser or adapter failures should be fixed in the relevant sibling parser repository, not in `yini-test-suite`, unless the shared case corpus or runner contract is wrong.
- Record known parser conformance gaps separately instead of hiding them in the corpus.

If building or checking a distribution locally, install the packaging tools in
your active environment first:

```bash
python -m pip install --upgrade build twine
```

Then build the distribution:

```bash
python -m build
```

Check built package metadata:

```bash
python -m twine check dist/*
```

Upload manually to PyPI:

```bash
python -m twine upload dist/*
```

When prompted, use:

```text
Username: __token__
Password: <your PyPI API token>
```

Prefer a project-scoped PyPI API token for `yini-test-suite`.

Only publish from a clean, intentional release process. PyPI versions are
immutable, so if an uploaded version needs a fix, bump the version number.

## Testing the package

Install the new package:
```bash
python -m pip install --upgrade yini-test-suite
```

Then verify the version with:
```bash
yini-test-suite --help
```

And verify the module entry point still works:
Then verify the version with:
```bash
python -m yini_test --help
```

## Final Gate

Before handing off a maintainer change, make sure:
- The smallest relevant checks have passed.
- Documentation matches visible CLI and runner behavior.
- Case-corpus changes obey `docs/case-contract.md`.
- Adapter-facing changes obey `docs/adapter-contract.md`.
- Setup and command changes are reflected in `docs/Development-Setup.md`.
- Any checks that could not be run are clearly called out.

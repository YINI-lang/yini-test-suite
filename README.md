# yini-test-suite

[![Tests](https://github.com/YINI-lang/yini-test-suite/actions/workflows/run-tests-fast.yml/badge.svg?branch=main)](https://github.com/YINI-lang/yini-test-suite/actions/workflows/run-tests-fast.yml)
[![PyPI version](https://img.shields.io/pypi/v/yini-test-suite)](https://pypi.org/project/yini-test-suite/)

`yini-test-suite` is a command-line tool and shared collection of test cases for
YINI parser implementations. Use it when building or testing a YINI parser.

It runs your parser through a small adapter program, compares the results with
the expected JSON, and checks warnings and invalid inputs. Each case is reported
as `PASS` or `FAIL`.

The same test cases can be used with parsers written in different languages.

## YINI specification targets

Choose a suite version that targets the YINI specification your parser implements:

| yini-test-suite version | YINI specification target |
| --- | --- |
| `0.4.0rc1` | [1.0.0-RC.7](https://github.com/YINI-lang/YINI-spec/blob/f1c2381309a65325021ba5b99922fa3855e9e4a8/YINI-Specification.md) |
| `0.3.0rc2` | [1.0.0-RC.6x](https://github.com/YINI-lang/YINI-spec/blob/fa6d1c7c7005fac483085b100f3095a049d71555/YINI-Specification.md) — earlier RC.7 draft expectations |
| `0.3.0rc1` | [1.0.0-RC.6](https://github.com/YINI-lang/YINI-spec/blob/v1.0.0-rc.6/YINI-Specification.md) |

Suite and specification versions are independent. The links above identify fixed
specification snapshots, including the earlier draft. The packaged
[case manifest](./src/yini_test/cases/manifest.json) records the current target.
The runner prints that target in its summary.

The unreleased source corpus targets `1.0.0-RC.7x` and includes the former
`upcoming` cases in normal suite runs. Released suite versions retain the
targets listed above.

---

## 📦 Install

Requires Python 3.10 or newer.

```bash
python -m pip install yini-test-suite
```

To include release candidates such as `0.4.0rc1`, use:

```bash
python -m pip install --pre yini-test-suite
```

To select a version from the table, use `yini-test-suite==<version>` in the
install command.

Check that the CLI is available:

```bash
yini-test-suite --help
```

The installed package includes the smoke and golden test cases. Use
`--cases-root` only when you want to run a different collection of cases.

---

## 🚀 Basic Usage

Get an adapter from the parser implementation you want to test. To run the
smaller smoke suite, replace `path/to/adapter.py` with your adapter's path:

```bash
yini-test-suite smoke --adapter python path/to/adapter.py --input "{input}" --mode "{mode}"
```

Run all bundled cases in both lenient and strict mode:

```bash
yini-test-suite all --all-modes --adapter python path/to/adapter.py --input "{input}" --mode "{mode}"
```

Important: `--adapter` must be the last `yini-test-suite` option. Everything
after `--adapter` is treated as part of the adapter command.

The runner replaces:
- `{input}` with the current `.yini` case path.
- `{mode}` with `lenient` or `strict`.

Use `--show-progress` if you also want a `RUN` line before each case:

```bash
yini-test-suite all --all-modes --show-progress --adapter python path/to/adapter.py --input "{input}" --mode "{mode}"
```

The double quotes around the placeholders make these commands work in Bash,
PowerShell, and Windows Command Prompt.

Use `--fail-fast` to stop after the first failing case. Put it before `--adapter`,
like the other runner options.

---

## 🧪 Suites and modes

Suites:
- `smoke` runs a small set of cases for a quick check.
- `golden` runs a larger set of cases with fixed expected results.
- `all` runs both suites and is the default when no suite is specified.

Modes:
- Lenient mode is the default.
- `--strict` runs strict-mode cases.
- `--all-modes` runs both lenient and strict mode and prints one combined summary.

---

## 🔌 Adapter Contract

An adapter is a small command-line program maintained with a parser. It accepts
an input file and parser mode, writes one JSON result to `stdout` on success,
and writes warnings or errors to `stderr`. It must return a non-zero exit code
when parsing fails.

The expected shape is:

```bash
adapter --input <path-to-yini-file> --mode <lenient|strict>
```

For details, see [docs/adapter-contract.md](./docs/adapter-contract.md).

---

## Examples with official parsers

Parser-specific adapter scripts are maintained in their parser repositories, not
in this runner package.

This repository provides example commands and Taskfile tasks for
[`yini-parser-typescript`](https://github.com/YINI-lang/yini-parser-typescript),
[`yini-parser-python`](https://github.com/YINI-lang/yini-parser-python),
and [`yini-parser-go`](https://github.com/YINI-lang/yini-parser-go).
Those examples require the corresponding sibling repository and its adapter;
they are not included in an installed `yini-test-suite` package.

For these examples, place the parser repositories alongside this repository:

```text
YINI-lang-WORK/
  yini-test-suite/
  yini-parser-typescript/
  yini-parser-python/
  yini-parser-go/
```

Follow each parser repository's setup instructions first. Run the commands below
from the `yini-test-suite` repository root. The direct TypeScript command assumes
its adapter has already been built.

Example TypeScript adapter command:

```bash
yini-test-suite all --all-modes --adapter node ../yini-parser-typescript/dist-tools/tools/yini-test-adapter.js --input "{input}" --mode "{mode}"
```

Example Python adapter command:

```bash
yini-test-suite all --all-modes --adapter python ../yini-parser-python/tools/yini_parser_adapter.py --input "{input}" --mode "{mode}"
```

When working from the source repository, the matching Taskfile commands are:

```bash
task run-all-typescript
task run-all-python
task run-all-go
```

The TypeScript and Go tasks build their adapters before running cases. The Go
tasks require Go 1.22 or newer and write the adapter to this repository's `build/`
directory.

If these runs expose parser or adapter problems, fix those issues in the
corresponding parser repository unless the shared case corpus or runner contract
is wrong.

---

## Output

A run starts with the runner name and version:

```text
yini-test-suite 0.4.0rc1
```

Each case is reported as `PASS` or `FAIL`, followed by a final summary.
Example summary header (the adapter and parser version depend on what you run):

```text
YINI Test Suite Summary
yini-test-suite: 0.4.0rc1
Adapter: yini-parser-typescript
Parser version: 1.7.0
YINI spec: 1.0.0-RC.7x
Test suite: "all"
```

For valid cases, the runner compares the adapter JSON output with the matching
expected `.json` file. Warning cases also check expected warning diagnostics.
Invalid cases are expected to fail.

The command exits with code `0` when all selected cases pass. It returns a
non-zero exit code if any case fails or the run cannot complete, so it can be
used in CI.

---

## Scope

This package provides the runner and test cases. Parsers and their adapters live
in separate repositories. The `yini_test` Python modules are internal; they are
not intended as a stable public library API.

---

## 🛠️ Development

For source checkout setup, Taskfile commands, local adapter runs, build checks,
and troubleshooting, see [docs/Development-Setup.md](./docs/Development-Setup.md).

Useful maintainer references:
- [docs/case-contract.md](./docs/case-contract.md)
- [docs/adapter-contract.md](./docs/adapter-contract.md)
- [docs/runner-flow.md](./docs/runner-flow.md)
- [docs/Maintainer-Doc.md](./docs/Maintainer-Doc.md)

After following the development setup, run `task check` before submitting a
change. Those checks test the runner itself. Use the adapter tasks above to test
parser behavior against the shared cases.

---

## License

Licensed under the [Apache License 2.0](./LICENSE).

---

## 💬 Help, feedback, and issues

For bugs, feedback, or other issues with `yini-test-suite`,
[open an issue](https://github.com/YINI-lang/yini-test-suite/issues).

For general YINI information, see:
- [YINI homepage](https://yini-lang.org/?utm_source=github&utm_campaign=yini_test&utm_content=readme_project_links&utm_medium=referral)
- [YINI GitHub organization](https://github.com/YINI-lang)
- [`yini-test-suite` repository](https://github.com/YINI-lang/yini-test-suite)

---

## About YINI

YINI is a human-readable, INI-inspired, indentation-insensitive configuration
format with clear nested sections, explicit structure, and predictable parsing.

[yini-lang.org](https://yini-lang.org/?utm_source=github&utm_campaign=yini_test&utm_content=readme_footer&utm_medium=referral) |
[YINI-lang on GitHub](https://github.com/YINI-lang)

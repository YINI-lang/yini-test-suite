# yini-test-suite

`yini-test-suite` is the shared command-line test runner and case corpus for
YINI parser implementations.

It does not parse YINI itself. Instead, it calls a parser implementation through
an adapter, compares the parser output with the expected JSON for each case, and
reports pass/fail results consistently.

The goal is to give different YINI parsers the same conformance target.

## Install

```bash
python -m pip install yini-test-suite
```

Check that the CLI is available:

```bash
yini-test-suite --help
```

The package includes the shared smoke and golden case corpus, so normal installed
usage does not require a separate `--cases-root` path.

## Basic Usage

Run the smoke suite against a parser adapter:

```bash
yini-test-suite smoke --adapter python path/to/adapter.py --input {input} --mode {mode}
```

Run all bundled cases in both lenient and strict mode:

```bash
yini-test-suite all --all-modes --adapter python path/to/adapter.py --input {input} --mode {mode}
```

Important: `--adapter` must be the last `yini-test-suite` option. Everything
after `--adapter` is treated as part of the adapter command.

The runner replaces:
- `{input}` with the current `.yini` case path.
- `{mode}` with `lenient` or `strict`.

Use `--show-progress` if you also want a `RUN` line before each case:

```bash
yini-test-suite all --all-modes --show-progress --adapter python path/to/adapter.py --input {input} --mode {mode}
```

## Suites And Modes

Suites:
- `smoke` runs a smaller confidence suite.
- `golden` runs the broader fixed-output conformance suite.
- `all` runs both `smoke` and `golden`.

Modes:
- Lenient mode is the default.
- `--strict` runs strict-mode cases.
- `--all-modes` runs both lenient and strict mode and prints one combined summary.

## Adapter Contract

An adapter is a small command-line program owned by a parser implementation. It
accepts an input file and parser mode, then prints parsed JSON to `stdout` on
success or diagnostics to `stderr` on failure.

The expected shape is:

```bash
adapter --input <path-to-yini-file> --mode <lenient|strict>
```

For details, see [docs/adapter-contract.md](./docs/adapter-contract.md).

## Official Ecosystem Examples

Parser-specific adapter scripts are maintained in their parser repositories, not
in this runner package.

However, this project provides official adapter integrations for
`yini-parser-typescript` and `yini-parser-python` through ready-made command
examples and Taskfile tasks. They are included to show working examples and
because those parsers are part of the official YINI ecosystem.

The expected sibling repository layout for those examples is:

```text
YINI-lang-WORK/
  yini-test-suite/
  yini-parser-typescript/
  yini-parser-python/
```

Example TypeScript adapter command:

```bash
yini-test-suite all --all-modes --adapter node ../yini-parser-typescript/dist-tools/tools/yini-test-adapter.js --input {input} --mode {mode}
```

Example Python adapter command:

```bash
yini-test-suite all --all-modes --adapter python ../yini-parser-python/tools/yini_parser_adapter.py --input {input} --mode {mode}
```

When working from the source repository, the matching Taskfile commands are:

```bash
task run-all-typescript
task run-all-python
```

If these runs expose parser or adapter problems, fix those issues in the
corresponding parser repository unless the shared case corpus or runner contract
is wrong.

## Output

A run starts with the runner name and version:

```text
yini-test-suite 0.3.0b2
```

Each case is reported as `PASS` or `FAIL`, followed by a final summary:

```text
YINI Test Suite Summary
yini-test-suite: 0.3.0b2
Adapter: yini-parser-typescript
Parser version: 1.6.1
YINI spec: 1.0.0 RC 6
Test suite: "all"
```

For valid cases, the runner compares the adapter JSON output with the matching
expected `.json` file. Warning cases also check expected warning diagnostics.
Invalid cases are expected to fail.

## What This Package Does Not Do

- It does not contain a YINI parser.
- It does not define parser-specific parsing behavior.
- It does not make parser-specific adapters part of the public `yini-test-suite`
  Python API.

## Development

For source checkout setup, Taskfile commands, local adapter runs, build checks,
and troubleshooting, see [docs/Development-Setup.md](./docs/Development-Setup.md).

Useful maintainer references:
- [docs/case-contract.md](./docs/case-contract.md)
- [docs/adapter-contract.md](./docs/adapter-contract.md)
- [docs/runner-flow.md](./docs/runner-flow.md)
- [docs/Maintainer-Doc.md](./docs/Maintainer-Doc.md)

## About YINI

YINI is a human-readable, INI-inspired, indentation-insensitive configuration
format with clear nested sections, explicit structure, and predictable parsing.

[yini-lang.org](https://yini-lang.org/?utm_source=github&utm_medium=referral&utm_campaign=yini_test&utm_content=readme_footer) |
[YINI-lang on GitHub](https://github.com/YINI-lang)

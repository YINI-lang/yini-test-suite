# CHANGELOG

**Changelog** for `yini-test-suite`.

## Upcomming
- **Fixed:** Updated case expectations for the RC.6x / RC.7 WIP specification: duplicate sections and mode-declaration mismatches now require parsing to fail.
- **Fixed:** Corrected nine JSON expectations to use LF for source line endings in multiline string values.
- **Fixed:** Restored mixed line endings in two fixtures and added Git attributes and regression tests to preserve their source bytes.
- **Added:** Golden cases for backslash escapes in **backticked keys and section names** (`\\` -> `\`) in lenient and strict modes.
- **Added:** Lenient and strict golden cases for lowercase, uppercase, and mixed-case Boolean and null spellings as distinct inline object key names.
- **Added:** Lenient and strict golden cases for `//`, `#`, and `/* ... */` comments after spaced, compact, and numeric shorthand section headers, plus invalid cases for trailing `;` comments.
- **Added:** Required warning checks for four lenient-mode cases with missing values interpreted as `null`.

## 0.3.0rc1 - 2026 September
- **Added:** Golden fixtures for CR and LF -only line endings in strict mode, and strict-mode rejection of token-splitting comments and raw control characters.
- **Added:** Golden fixtures that verify control markers remain string content and duplicate keys are scoped to their containing sections and inline objects in both parser modes.
- **Fixed:** JSON expectation and adapter output validation now reject non-standard `NaN` and infinity values.
- **Fixed:** JSON comparisons now distinguish booleans from numbers, so `true` no longer matches `1`.
- **Fixed:** Empty selected suite/mode groups now fail instead of reporting a false passing result with zero cases.
- **Changed:** Updated case and adapter documentation to describe warning cases accurately, reserve the future `edge` suite, and correct the adapter-contract link.
- **Added:** Regression coverage for strict JSON validation, JSON type comparisons, warning-case mismatches, and empty suite groups.

## 0.3.0b2 - 2026 July
- **Changed:** CLI help now prints the `yini-test-suite` name and version above the usage line.
- **Changed:** Runner output now prints the `yini-test-suite` name and version before case processing starts.

## 0.3.0b1 - 2026 July
- **Added:** Golden section cases for alternate markers, shorthand depths, separator forms, whitespace handling, and invalid marker/level jumps.
- **Added:** Golden string cases for raw/classic prefixes, quote variants, triple-quoted strings, Unicode text, Windows paths, and invalid string forms.
- **Added:** Added option `--show-progress` to also print a `RUN` line before each case executes.

## 0.1.0a3
- **Added:** Runner output now includes a summary table and result status, with passed/failed/total counts per suite and mode.

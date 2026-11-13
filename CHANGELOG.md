# CHANGELOG

**Changelog** for `yini-test-suite`.

## Upcoming
- **Fixed:** Aligned mode-declaration cases with the latest RC.6x / RC.7 WIP rules: `@yini lenient` in strict mode now requires a warning and successful strict validation; `@yini strict` in lenient mode still requires rejection.
- **Added:** Strict invalid cases with a lenient declaration and either a trailing list comma or a missing `/END` terminator.
- **Added:** Deprecation-warning checks for `%` binary literals in both modes and in lenient concatenation. Existing parsed values are unchanged.
- **Added:** A case with regression coverage for an inline-object key named `hex` using compact `hex:10` syntax in both modes, expecting decimal `10` while retaining hexadecimal-prefix coverage.

## 0.3.0rc2 - 2026 November
- **Fixed:** Updated case expectations for the RC.6x / RC.7 WIP specification: duplicate sections and mode-declaration mismatches now require parsing to fail.
- **Fixed:** Corrected nine JSON expectations to use LF for source line endings in multiline string values.
- **Fixed:** Restored mixed line endings in two fixtures and added Git attributes and regression tests to preserve their source bytes.
- **Fixed:** CRLF, LF, and CR fixtures are now pinned in `.gitattributes` so Git cannot convert their line endings. Previously, the CRLF fixtures were stored with LF, so on non-Windows checkouts they did not test CRLF. A corpus test now checks the line endings of each such fixture.
- **Changed:** Lenient misplaced-shebang and mixed-line-ending cases now live under `warning/` and require a warning. SHOULD-level warnings are required by this corpus; see `docs/case-contract.md`.
- **Changed:** Renamed misleading cases, clarified `key-using-colon` so the colon is its only error, and removed duplicate cases.
- **Added:** Golden cases for backslash escapes in **backticked keys and section names** (`\\` -> `\`) in lenient and strict modes.
- **Added:** Lenient and strict golden cases for lowercase, uppercase, and mixed-case Boolean and null spellings as distinct inline object key names.
- **Added:** Lenient and strict golden cases for `//`, `#`, and `/* ... */` comments after spaced, compact, and numeric shorthand section headers, plus invalid cases for trailing `;` comments.
- **Added:** Required warning checks for four lenient-mode cases with missing values interpreted as `null`.
- **Added:** Golden cases for important RC.7 and edge behavior: `#` after `=`, line breaks inside block comments, `\xhh` and other escapes, CRLF in triple-quoted strings, backticked-identifier restrictions, the `>` marker, hexadecimal 64-bit limits, empty object slots, duplicate `/END`, reserved `@include`, curly-quote delimiters, and invalid UTF-8.
- **Added:** Golden cases for comma-only collections, `key = ,`, section names reused under different parents, backticked-key duplicates and significant spaces, surrogate escapes, `.5`, underscore section names, missing values followed by comments, uncommon escapes, section depth 256, Unicode whitespace, misplaced digit separators, malformed `hex:` forms, and numeric addition.
- **Added:** Regression tests for harness behavior covering invalid-case exit codes, warning enforcement, adapter timeouts, malformed JSON output, and `--fail-fast` execution and summary counts.
- **Added:** End-to-end CLI tests using a temporary adapter to verify parser modes, paths containing spaces, Unicode output, summaries, and process exit codes.

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

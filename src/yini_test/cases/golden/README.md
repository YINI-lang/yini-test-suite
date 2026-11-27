# Golden Case Fixtures

This document summarizes the general characteristics of the golden test fixtures. Golden tests are more detailed, representative test cases that cover all major YINI features and expected parser behavior.

These golden fixtures are organized into the following directory structure:
```txt
golden/<mode>/<expected>/<category>/<fixture-files...>
```

Where:
- **mode** is either `lenient` or `strict`, indicating the parser mode used, when parsing a fixture.
- **expected** is `valid`, `warning`, or `invalid`, and defines whether the fixture succeeds, succeeds with expected diagnostics, or fails.
- **category** is the feature group being tested.
- **fixture-files** are the `.yini` files in that category. Each file covers a group of related cases for a specific feature type.

## Scope

Golden fixtures define stable input/output expectations for selected YINI syntax and behavior.

Golden tests SHOULD provide broad coverage of **all major** YINI features through representative cases, rather than exhaustively mapping every isolated syntax variation to its own expected result.

These fixtures aim to cover more detailed syntax sets and behavior cases of specific types of features within each category.

Yet more exhaustive and specification-level coverage should be handled by dedicated ***future*** conformance tests.

## RC.7x Expectations

These cases run as part of the normal golden and full suites. The corpus target
is declared in [the case manifest](../manifest.json).

Missing and comment-only assignment values must fail in both modes.
Case-insensitive `None` is a null alias; `null` remains the canonical spelling.
Neither `-` nor `~` is a null alias. Null cases also cover case-sensitive keyword
keys, quoted strings, empty strings and collections, and canonical `null`
conversion in lenient concatenation.

Empty sections are valid in both modes. Their cases deliberately require the
recommended warning, following [the case contract](../../../../docs/case-contract.md).
The specification uses SHOULD for that warning, so its absence alone does not
make the YINI document invalid. Parents containing subsections are not empty.

Block String cases use the `b` and `block` prefixes. The former `command` prefix
must fail in both modes. Valid cases cover structural indentation, blank lines,
literal tabs, LF normalization for LF, CRLF, and CR, comments after closing
quotes, and comments after concatenation operators and list commas.

Each mode has 29 invalid control-character cases for Block Strings, one for each literal character from
`U+0000` through `U+001F` except tab, LF, and CR. Each file contains one forbidden
character between `second` and `part`. The hexadecimal code point appears in
the filename. Preserve the literal bytes when editing these files.

A parser must pass valid Block String cases before its rejection of invalid
Block Strings can demonstrate the control-character rule. A parser that rejects
the prefix will also reject those invalid cases.

---

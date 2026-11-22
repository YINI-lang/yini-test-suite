# Upcoming Block String cases

These 64 golden cases cover the agreed Block String control-character rules
for the upcoming YINI specification. They use the `b` prefix.

Each parsing mode has three valid cases. Their source line endings are LF,
CRLF, and CR. Each expects LF between content lines and preserves literal tabs
after removing the ASCII-space margin.

Each mode also has 29 invalid cases, one for each literal character from
`U+0000` through `U+001F` except tab, LF, and CR. Each file contains one
forbidden character between `second` and `part`. The hexadecimal code point
appears in the filename. Preserve the literal bytes when editing these files.

Run these cases from the repository root with a Python parser checkout that
supports Block Strings.

~~~sh
python -m yini_test golden --all-modes --cases-root src/yini_test/cases/upcoming --adapter python ../yini-parser-python/tools/yini_parser_adapter.py --input "{input}" --mode "{mode}"
~~~

Other parser adapters can use the same cases root. The runner's summary
currently reports the packaged corpus revision, RC.7, even with a custom
cases root. This directory contains upcoming expectations.

A parser must pass the valid cases before its rejection of the invalid cases
can demonstrate the control-character rule. A parser that rejects the `b`
prefix will also reject every invalid case.

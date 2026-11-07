from pathlib import Path
import re

import pytest


@pytest.mark.parametrize(
    "case_path",
    [
        "golden/lenient/warning/encoding/mixed-line-endings.yini",
        "golden/strict/invalid/encoding/mixed-line-endings.strict.yini",
    ],
)
def test_mixed_line_ending_cases_contain_multiple_source_line_endings(
    case_path: str,
) -> None:
    cases_root = Path(__file__).resolve().parents[1] / "src/yini_test/cases"
    source = (cases_root / case_path).read_bytes()

    line_endings = set(re.findall(rb"\r\n|\r|\n", source))

    assert len(line_endings) > 1, f"Fixture has no mixed line endings: {case_path}"


@pytest.mark.parametrize(
    ("case_path", "expected_line_ending"),
    [
        ("golden/lenient/valid/encoding/lf-line-endings.yini", b"\n"),
        ("golden/strict/valid/encoding/lf-line-endings.strict.yini", b"\n"),
        ("golden/lenient/valid/encoding/crlf-line-endings.yini", b"\r\n"),
        ("golden/strict/valid/encoding/crlf-line-endings.strict.yini", b"\r\n"),
        ("golden/lenient/valid/encoding/cr-line-endings.yini", b"\r"),
        ("golden/strict/valid/encoding/cr-line-endings.strict.yini", b"\r"),
        ("golden/lenient/valid/strings/command-string-crlf.yini", b"\r\n"),
        ("golden/strict/valid/strings/command-string-crlf.strict.yini", b"\r\n"),
        ("golden/lenient/valid/strings/raw-triple-quoted-crlf-source.yini", b"\r\n"),
        (
            "golden/strict/valid/strings/raw-triple-quoted-crlf-source.strict.yini",
            b"\r\n",
        ),
        ("golden/lenient/valid/strings/raw-triple-quoted-cr-source.yini", b"\r"),
        ("golden/strict/valid/strings/raw-triple-quoted-cr-source.strict.yini", b"\r"),
        (
            "golden/lenient/valid/strings/escaped-triple-quoted-crlf-source.yini",
            b"\r\n",
        ),
        (
            "golden/strict/valid/strings/escaped-triple-quoted-crlf-source.strict.yini",
            b"\r\n",
        ),
    ],
)
def test_single_line_ending_cases_use_only_their_line_ending(
    case_path: str,
    expected_line_ending: bytes,
) -> None:
    cases_root = Path(__file__).resolve().parents[1] / "src/yini_test/cases"
    source = (cases_root / case_path).read_bytes()

    line_endings = set(re.findall(rb"\r\n|\r|\n", source))

    assert line_endings == {expected_line_ending}, (
        f"Fixture does not use only {expected_line_ending!r} line endings: {case_path}"
    )

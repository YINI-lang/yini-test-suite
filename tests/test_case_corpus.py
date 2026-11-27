import json
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
        ("golden/lenient/valid/strings/block-string-crlf.yini", b"\r\n"),
        ("golden/strict/valid/strings/block-string-crlf.strict.yini", b"\r\n"),
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


@pytest.mark.parametrize("mode", ["lenient", "strict"])
@pytest.mark.parametrize(
    ("ending_name", "line_ending"),
    [("lf", b"\n"), ("crlf", b"\r\n"), ("cr", b"\r")],
)
def test_block_string_valid_fixture_bytes(
    mode: str, ending_name: str, line_ending: bytes
) -> None:
    # 1. Arrange.
    cases_root = Path(__file__).resolve().parents[1] / "src/yini_test/cases"
    suffix = ".strict" if mode == "strict" else ""
    folder = cases_root / "golden" / mode / "valid/strings"
    case = folder / f"block-string-tabs-{ending_name}{suffix}.yini"

    # 2. Act.
    source = case.read_bytes()
    expected = json.loads(case.with_suffix(".json").read_bytes())

    # 3. Assert.
    assert set(re.findall(rb"\r\n|\r|\n", source)) == {line_ending}
    assert b"  \tfirst" + line_ending + b"  second\tpart" in source
    assert expected == {"Strings": {"text": "\tfirst\nsecond\tpart"}}


@pytest.mark.parametrize("mode", ["lenient", "strict"])
def test_block_string_invalid_fixtures_cover_each_control(mode: str) -> None:
    # 1. Arrange.
    cases_root = Path(__file__).resolve().parents[1] / "src/yini_test/cases"
    folder = cases_root / "golden" / mode
    suffix = ".strict" if mode == "strict" else ""
    valid = folder / "valid/strings" / f"block-string-tabs-lf{suffix}.yini"
    forbidden = set(range(32)) - {9, 10, 13}

    # 2. Act.
    baseline = valid.read_bytes()
    invalid = {
        path.name: path.read_bytes()
        for path in (folder / "invalid/strings").glob("block-string-u*.yini")
    }

    # 3. Assert.
    assert set(invalid) == {
        f"block-string-u{code_point:04x}{suffix}.yini" for code_point in forbidden
    }
    for code_point in forbidden:
        name = f"block-string-u{code_point:04x}{suffix}.yini"
        expected = baseline.replace(
            b"second\tpart", b"second" + bytes([code_point]) + b"part"
        )
        assert invalid[name] == expected, name

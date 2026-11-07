from pathlib import Path
import re

import pytest


@pytest.mark.parametrize(
    "case_path",
    [
        "golden/lenient/valid/encoding/mixed-line-endings.yini",
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

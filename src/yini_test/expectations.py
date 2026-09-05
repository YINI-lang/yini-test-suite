"""
Expected-output and warning-matching helpers for yini_test.
"""

# src/yini_test/expectations.py
from __future__ import annotations

from pathlib import Path
import json
from typing import Any


def _reject_non_standard_json_constant(value: str) -> None:
    """Reject values that Python accepts but JSON does not define."""

    raise ValueError(f"Non-standard JSON value: {value}")


def load_expected_json(path: Path) -> Any:
    """
    Load an expected JSON file.

    The file may contain a UTF-8 BOM. Using utf-8-sig accepts both normal
    UTF-8 and UTF-8 with BOM.
    """

    try:
        with path.open("r", encoding="utf-8-sig") as f:
            return json.load(f, parse_constant=_reject_non_standard_json_constant)
    except (json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(
            "Expected JSON file is not valid JSON.\n"
            f'  json_path: "{path}"\n'
            f"  error: {exc}"
        ) from exc


def load_expected_warnings(path: Path) -> list[dict[str, Any]]:
    """
    Load expected warning diagnostics for a warning case.

    Initial warning format:

        [
            {
                "contains": "YINI_MODE_MISMATCH"
            }
        ]
    """

    warnings_data = load_expected_json(path)

    if not isinstance(warnings_data, list):
        raise RuntimeError(
            "Expected warning file must contain a JSON array.\n"
            f'  warning_path: "{path}"'
        )

    for index, item in enumerate(warnings_data):
        if not isinstance(item, dict):
            raise RuntimeError(
                "Each expected warning entry must be a JSON object.\n"
                f'  warning_path: "{path}"\n'
                f"  index: {index}"
            )

        if "contains" not in item:
            raise RuntimeError(
                "Each expected warning entry must contain a 'contains' field.\n"
                f'  warning_path: "{path}"\n'
                f"  index: {index}"
            )

        if not isinstance(item["contains"], str):
            raise RuntimeError(
                "The expected warning 'contains' field must be a string.\n"
                f'  warning_path: "{path}"\n'
                f"  index: {index}"
            )

    return warnings_data


def json_values_match(expected: Any, actual: Any) -> bool:
    """Compare JSON values without treating booleans as numbers.

    Python considers ``True == 1`` and ``False == 0``. Those values have
    different meanings in JSON, so comparisons must keep their types distinct.
    Integer and floating-point numbers remain comparable by numeric value,
    matching the JSON number data model.
    """

    if isinstance(expected, dict):
        if not isinstance(actual, dict) or expected.keys() != actual.keys():
            return False

        return all(json_values_match(expected[key], actual[key]) for key in expected)

    if isinstance(expected, list):
        if not isinstance(actual, list) or len(expected) != len(actual):
            return False

        return all(
            json_values_match(expected_item, actual_item)
            for expected_item, actual_item in zip(expected, actual)
        )

    if isinstance(expected, bool) or isinstance(actual, bool):
        return type(expected) is type(actual) and expected == actual

    if expected is None or actual is None:
        return expected is actual

    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return expected == actual

    return type(expected) is type(actual) and expected == actual


def match_expected_warnings(
    expected_warnings: list[dict[str, Any]],
    stderr: str,
) -> str | None:
    """
    Check that every expected warning marker appears in stderr.

    Returns None when all expected warnings match.
    Returns an error message otherwise.
    """

    for expected_warning in expected_warnings:
        expected_text = expected_warning["contains"]

        if expected_text not in stderr:
            return (
                "Expected warning text was not found.\n"
                f"  expected contains: {expected_text!r}"
            )

    return None

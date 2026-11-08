# tests/test_runner.py
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from yini_test.adapters import parse_adapter_stdout_json, render_adapter_command
from yini_test.diffing import make_diff
from yini_test.discovery import (
    discover_invalid_cases,
    discover_valid_cases,
    get_expected_json_path,
)
from yini_test.expectations import json_values_match, load_expected_json
from yini_test.models import (
    AdapterResult,
    CaseResult,
    InvalidCase,
    ValidCase,
    WarningCase,
)
from yini_test.runner import (
    detect_parser_version,
    format_adapter_name,
    format_summary_rule,
    get_yini_spec_revision,
    run_case_group,
    run_invalid_case,
    run_valid_case,
    run_warning_case,
    run_suite,
    run_suite_matrix,
    _resolve_suite_names,
)


def test_get_expected_json_path_returns_matching_json_path(tmp_path: Path) -> None:
    # Arrange.
    yini_path = tmp_path / "basic-config.yini"
    json_path = tmp_path / "basic-config.json"

    yini_path.write_text('name = "Demo"', encoding="utf-8")
    json_path.write_text('{"name": "Demo"}', encoding="utf-8")

    # Act.
    result = get_expected_json_path(yini_path)

    # Assert.
    assert result == json_path


def test_get_expected_json_path_raises_clear_error_when_json_file_is_missing(
    tmp_path: Path,
) -> None:
    # Arrange.
    yini_path = tmp_path / "missing-json.yini"
    expected_json_path = tmp_path / "missing-json.json"

    yini_path.write_text('name = "Demo"', encoding="utf-8")

    # Act.
    with pytest.raises(FileNotFoundError) as exc_info:
        get_expected_json_path(yini_path)

    # Assert.
    message = str(exc_info.value)

    assert "Expected JSON file not found for YINI case." in message
    assert f'yini_path: "{yini_path}"' in message
    assert f'expected_json_path: "{expected_json_path}"' in message
    assert "matching .json file" in message


def test_discover_valid_cases_returns_yini_json_pairs(tmp_path: Path) -> None:
    # Arrange.
    valid_dir = tmp_path / "valid"
    valid_dir.mkdir()

    first_yini = valid_dir / "1-basic.yini"
    first_json = valid_dir / "1-basic.json"

    second_yini = valid_dir / "2-nested.yini"
    second_json = valid_dir / "2-nested.json"

    first_yini.write_text('name = "Demo"', encoding="utf-8")
    first_json.write_text(json.dumps({"name": "Demo"}), encoding="utf-8")

    second_yini.write_text('^ App\nname = "Demo"', encoding="utf-8")
    second_json.write_text(json.dumps({"App": {"name": "Demo"}}), encoding="utf-8")

    # Act.
    cases = discover_valid_cases(valid_dir)

    # Assert.
    assert cases == [
        ValidCase(yini_path=first_yini, json_path=first_json),
        ValidCase(yini_path=second_yini, json_path=second_json),
    ]


def test_discover_valid_cases_returns_empty_list_when_directory_is_missing(
    tmp_path: Path,
) -> None:
    # Arrange.
    valid_dir = tmp_path / "valid"

    # Act.
    cases = discover_valid_cases(valid_dir)

    # Assert.
    assert cases == []


def test_discover_valid_cases_raises_when_path_is_not_directory(
    tmp_path: Path,
) -> None:
    # Arrange.
    valid_dir = tmp_path / "valid"
    valid_dir.write_text("not a directory", encoding="utf-8")

    # Act.
    with pytest.raises(NotADirectoryError) as exc_info:
        discover_valid_cases(valid_dir)

    # Assert.
    assert "Valid case path is not a directory" in str(exc_info.value)


def test_discover_invalid_cases_returns_yini_files(tmp_path: Path) -> None:
    # Arrange.
    invalid_dir = tmp_path / "invalid"
    invalid_dir.mkdir()

    first_yini = invalid_dir / "1-broken.yini"
    second_yini = invalid_dir / "2-invalid-section.yini"

    first_yini.write_text("=", encoding="utf-8")
    second_yini.write_text("^^ MissingParent", encoding="utf-8")

    # Act.
    cases = discover_invalid_cases(invalid_dir)

    # Assert.
    assert cases == [
        InvalidCase(yini_path=first_yini),
        InvalidCase(yini_path=second_yini),
    ]


def test_discover_invalid_cases_returns_empty_list_when_directory_is_missing(
    tmp_path: Path,
) -> None:
    # Arrange.
    invalid_dir = tmp_path / "invalid"

    # Act.
    cases = discover_invalid_cases(invalid_dir)

    # Assert.
    assert cases == []


def test_discover_invalid_cases_raises_when_path_is_not_directory(
    tmp_path: Path,
) -> None:
    # Arrange.
    invalid_dir = tmp_path / "invalid"
    invalid_dir.write_text("not a directory", encoding="utf-8")

    # Act.
    with pytest.raises(NotADirectoryError) as exc_info:
        discover_invalid_cases(invalid_dir)

    # Assert.
    assert "Invalid case path is not a directory" in str(exc_info.value)


def test_render_adapter_command_replaces_input_and_mode_placeholders(
    tmp_path: Path,
) -> None:
    # Arrange.
    input_path = tmp_path / "basic.yini"

    adapter_tokens = [
        "python",
        "adapter.py",
        "--input",
        "{input}",
        "--mode",
        "{mode}",
    ]

    # Act.
    command = render_adapter_command(
        adapter_tokens=adapter_tokens,
        input_path=input_path,
        mode="lenient",
    )

    # Assert.
    assert command == [
        "python",
        "adapter.py",
        "--input",
        str(input_path),
        "--mode",
        "lenient",
    ]


def test_render_adapter_command_raises_when_adapter_command_is_empty(
    tmp_path: Path,
) -> None:
    # Arrange.
    input_path = tmp_path / "basic.yini"

    # Act.
    with pytest.raises(ValueError) as exc_info:
        render_adapter_command(
            adapter_tokens=[],
            input_path=input_path,
            mode="lenient",
        )

    # Assert.
    assert "Adapter command is empty." in str(exc_info.value)


def test_make_diff_contains_expected_and_actual_output() -> None:
    # Arrange.
    expected = {"name": "Demo", "enabled": True}
    actual = {"name": "Demo", "enabled": False}

    # Act.
    diff = make_diff(expected, actual)

    # Assert.
    assert "--- expected" in diff
    assert "parser output" in diff
    assert '"enabled": true' in diff
    assert '"enabled": false' in diff
    assert "Mismatched block:" in diff


@pytest.mark.parametrize("content", ["NaN", "Infinity", "-Infinity"])
def test_load_expected_json_rejects_non_standard_json_constants(
    tmp_path: Path,
    content: str,
) -> None:
    # Arrange.
    json_path = tmp_path / "expected.json"
    json_path.write_text(content, encoding="utf-8")

    # Act and assert.
    with pytest.raises(RuntimeError, match="not valid JSON"):
        load_expected_json(json_path)


@pytest.mark.parametrize("output", ["NaN", "Infinity", "-Infinity"])
def test_parse_adapter_stdout_json_rejects_non_standard_json_constants(
    output: str,
) -> None:
    # Act and assert.
    with pytest.raises(RuntimeError, match="not valid JSON"):
        parse_adapter_stdout_json(output, case_name="case.yini")


def test_json_values_match_distinguishes_booleans_from_numbers() -> None:
    # Act and assert.
    assert not json_values_match({"enabled": True}, {"enabled": 1})
    assert not json_values_match([False], [0])
    assert json_values_match({"value": 1}, {"value": 1.0})


def test_resolve_suite_names_for_smoke() -> None:
    # Arrange.
    suite = "smoke"

    # Act.
    result = _resolve_suite_names(suite)

    # Assert.
    assert result == ["smoke"]


def test_resolve_suite_names_for_golden() -> None:
    # Arrange.
    suite = "golden"

    # Act.
    result = _resolve_suite_names(suite)

    # Assert.
    assert result == ["golden"]


def test_resolve_suite_names_for_all() -> None:
    # Arrange.
    suite = "all"

    # Act.
    result = _resolve_suite_names(suite)

    # Assert.
    assert result == ["smoke", "golden"]


def test_resolve_suite_names_raises_for_unknown_suite() -> None:
    # Arrange.
    suite = "unknown"

    # Act.
    with pytest.raises(ValueError) as exc_info:
        _resolve_suite_names(suite)

    # Assert.
    assert "Unsupported suite" in str(exc_info.value)


def test_run_suite_matrix_runs_groups_in_suite_then_mode_order(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Arrange.
    calls: list[tuple[str, str]] = []

    def fake_run_case_group(
        suite_name: str,
        mode: str,
        cases_root: Path,
        adapter_tokens: list[str],
        fail_fast: bool = False,
        show_progress: bool = False,
    ) -> list[CaseResult]:
        calls.append((suite_name, mode))
        return [
            CaseResult(
                case_path=tmp_path / f"{suite_name}-{mode}.yini",
                passed=True,
            )
        ]

    monkeypatch.setattr("yini_test.runner.run_case_group", fake_run_case_group)
    monkeypatch.setattr(
        "yini_test.runner.detect_parser_version",
        lambda adapter_tokens: "not detected",
    )

    # Act.
    exit_code = run_suite_matrix(
        suite="all",
        modes=["lenient", "strict"],
        cases_root=tmp_path,
        adapter_tokens=["adapter"],
    )

    # Assert.
    output = capsys.readouterr().out

    assert exit_code == 0
    assert output.startswith("yini-test-suite 0.3.0rc2\n")
    assert calls == [
        ("smoke", "lenient"),
        ("smoke", "strict"),
        ("golden", "lenient"),
        ("golden", "strict"),
    ]
    assert "YINI Test Suite Summary" in output
    assert "Adapter: adapter" in output
    assert "Parser version: not detected" in output
    assert "yini-test-suite: 0.3.0rc2" in output
    assert 'Test suite: "all"' in output
    assert "YINI spec: 1.0.0-RC.6x" in output
    assert "PASS  " in output
    assert "RUN   " not in output
    assert "smoke    lenient" in output
    assert "golden   strict" in output
    assert "Result:  PASS" in output
    assert "Summary: 4 passed, 0 failed, 4 total" in output
    assert output.index("yini-test-suite 0.3.0rc2") < output.index("PASS  ")
    assert output.index("YINI Test Suite Summary") < output.index(
        "yini-test-suite: 0.3.0rc2"
    )
    assert output.index("yini-test-suite: 0.3.0rc2") < output.index("Adapter: adapter")
    assert output.index("Adapter: adapter") < output.index(
        "Parser version: not detected"
    )
    assert output.index("Parser version: not detected") < output.index(
        "YINI spec: 1.0.0-RC.6x"
    )
    assert output.index("YINI spec: 1.0.0-RC.6x") < output.index('Test suite: "all"')


def test_run_suite_matrix_summary_lists_failed_groups(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Arrange.
    def fake_run_case_group(
        suite_name: str,
        mode: str,
        cases_root: Path,
        adapter_tokens: list[str],
        fail_fast: bool = False,
        show_progress: bool = False,
    ) -> list[CaseResult]:
        if suite_name == "golden" and mode == "strict":
            return [
                CaseResult(
                    case_path=tmp_path / "failing.yini",
                    passed=False,
                    message="Expected failure",
                )
            ]

        return [
            CaseResult(
                case_path=tmp_path / f"{suite_name}-{mode}.yini",
                passed=True,
            )
        ]

    monkeypatch.setattr("yini_test.runner.run_case_group", fake_run_case_group)
    monkeypatch.setattr(
        "yini_test.runner.detect_parser_version",
        lambda adapter_tokens: "1.6.0",
    )

    # Act.
    exit_code = run_suite_matrix(
        suite="all",
        modes=["lenient", "strict"],
        cases_root=tmp_path,
        adapter_tokens=[
            "node",
            "../yini-parser-typescript/dist-tools/tools/yini-test-adapter.js",
            "--input",
            "{input}",
            "--mode",
            "{mode}",
        ],
    )

    # Assert.
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "Adapter: yini-parser-typescript" in output
    assert "Parser version: 1.6.0" in output
    assert "yini-test-suite: 0.3.0rc2" in output
    assert 'Test suite: "all"' in output
    assert "YINI spec: 1.0.0-RC.6x" in output
    assert "Summary: 3 passed, 1 failed, 4 total" in output
    assert "Result:  FAIL" in output
    assert "Failed groups:" in output
    assert "- golden / strict: 1 failed" in output


def test_run_suite_matrix_show_progress_forwards_to_case_groups(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Arrange.
    show_progress_values: list[bool] = []

    def fake_run_case_group(
        suite_name: str,
        mode: str,
        cases_root: Path,
        adapter_tokens: list[str],
        fail_fast: bool = False,
        show_progress: bool = False,
    ) -> list[CaseResult]:
        show_progress_values.append(show_progress)
        return [
            CaseResult(
                case_path=tmp_path / f"{suite_name}-{mode}.yini",
                passed=True,
            )
        ]

    monkeypatch.setattr("yini_test.runner.run_case_group", fake_run_case_group)
    monkeypatch.setattr(
        "yini_test.runner.detect_parser_version",
        lambda adapter_tokens: "not detected",
    )

    # Act.
    exit_code = run_suite_matrix(
        suite="smoke",
        modes=["lenient"],
        cases_root=tmp_path,
        adapter_tokens=["adapter"],
        show_progress=True,
    )

    # Assert.
    assert exit_code == 0
    assert show_progress_values == [True]


def test_run_valid_case_hides_run_line_by_default(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Arrange.
    yini_path = tmp_path / "case.yini"
    json_path = tmp_path / "case.json"
    case = ValidCase(yini_path=yini_path, json_path=json_path)

    json_path.write_text('{"name": "Demo"}', encoding="utf-8")
    monkeypatch.setattr(
        "yini_test.runner.run_adapter",
        lambda adapter_tokens, input_path, mode: {"name": "Demo"},
    )

    # Act.
    result = run_valid_case(case, adapter_tokens=["adapter"], mode="lenient")

    # Assert.
    output = capsys.readouterr().out

    assert result.passed is True
    assert "RUN   " not in output


def test_run_valid_case_shows_run_line_with_show_progress(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Arrange.
    yini_path = tmp_path / "case.yini"
    json_path = tmp_path / "case.json"
    case = ValidCase(yini_path=yini_path, json_path=json_path)

    json_path.write_text('{"name": "Demo"}', encoding="utf-8")
    monkeypatch.setattr(
        "yini_test.runner.run_adapter",
        lambda adapter_tokens, input_path, mode: {"name": "Demo"},
    )

    # Act.
    result = run_valid_case(
        case,
        adapter_tokens=["adapter"],
        mode="lenient",
        show_progress=True,
    )

    # Assert.
    output = capsys.readouterr().out

    assert result.passed is True
    assert f'RUN   "{yini_path}"' in output


def test_run_valid_case_fails_when_boolean_is_returned_as_number(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Arrange.
    yini_path = tmp_path / "case.yini"
    json_path = tmp_path / "case.json"
    case = ValidCase(yini_path=yini_path, json_path=json_path)

    json_path.write_text('{"enabled": true}', encoding="utf-8")
    monkeypatch.setattr(
        "yini_test.runner.run_adapter",
        lambda adapter_tokens, input_path, mode: {"enabled": 1},
    )

    # Act.
    result = run_valid_case(case, adapter_tokens=["adapter"], mode="lenient")

    # Assert.
    assert result.passed is False
    assert "Output mismatch for valid case" in result.message


def test_run_warning_case_fails_when_boolean_is_returned_as_number(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Arrange.
    yini_path = tmp_path / "case.yini"
    json_path = tmp_path / "case.json"
    warning_path = tmp_path / "case.warning.json"
    case = WarningCase(
        yini_path=yini_path,
        json_path=json_path,
        warning_path=warning_path,
    )

    json_path.write_text('{"enabled": true}', encoding="utf-8")
    warning_path.write_text('[{"contains": "mode mismatch"}]', encoding="utf-8")
    monkeypatch.setattr(
        "yini_test.runner.run_adapter_raw",
        lambda adapter_tokens, input_path, mode: AdapterResult(
            stdout='{"enabled": 1}',
            stderr="mode mismatch",
            returncode=0,
        ),
    )

    # Act.
    result = run_warning_case(case, adapter_tokens=["adapter"], mode="strict")

    # Assert.
    assert result.passed is False
    assert "Output mismatch for warning case" in result.message


def test_run_case_group_returns_failure_for_empty_group(tmp_path: Path) -> None:
    # Arrange.
    suite_dir = tmp_path / "smoke" / "lenient"
    suite_dir.mkdir(parents=True)

    # Act.
    results = run_case_group(
        suite_name="smoke",
        mode="lenient",
        cases_root=tmp_path,
        adapter_tokens=["adapter"],
    )

    # Assert.
    assert len(results) == 1
    assert results[0].case_path == suite_dir
    assert results[0].passed is False
    assert (
        "No test cases were found for suite group: smoke / lenient"
        in results[0].message
    )


def test_run_suite_fails_for_empty_group(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Arrange.
    (tmp_path / "smoke" / "lenient").mkdir(parents=True)
    monkeypatch.setattr(
        "yini_test.runner.detect_parser_version",
        lambda adapter_tokens: "not detected",
    )

    # Act.
    exit_code = run_suite(
        suite="smoke",
        mode="lenient",
        cases_root=tmp_path,
        adapter_tokens=["adapter"],
    )

    # Assert.
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "No test cases were found for suite group: smoke / lenient" in output
    assert "Summary: 0 passed, 1 failed, 1 total" in output


def test_format_adapter_name_prefers_yini_parser_repository_name() -> None:
    # Arrange.
    adapter_tokens = [
        "node",
        "../yini-parser-typescript/dist-tools/tools/yini-test-adapter.js",
        "--input",
        "{input}",
    ]

    # Act.
    adapter_name = format_adapter_name(adapter_tokens)

    # Assert.
    assert adapter_name == "yini-parser-typescript"


def test_format_adapter_name_uses_script_name_after_runner_command() -> None:
    # Arrange.
    adapter_tokens = [
        "python",
        "tools/custom_adapter.py",
        "--input",
        "{input}",
    ]

    # Act.
    adapter_name = format_adapter_name(adapter_tokens)

    # Assert.
    assert adapter_name == "custom_adapter"


def test_detect_parser_version_reads_package_json(tmp_path: Path) -> None:
    # Arrange.
    parser_root = tmp_path / "yini-parser-typescript"
    adapter_path = parser_root / "dist-tools" / "tools" / "yini-test-adapter.js"
    adapter_path.parent.mkdir(parents=True)
    adapter_path.write_text("// adapter", encoding="utf-8")
    (parser_root / "package.json").write_text(
        json.dumps({"name": "yini-parser", "version": "1.6.0"}),
        encoding="utf-8",
    )

    # Act.
    version = detect_parser_version(["node", str(adapter_path), "--input", "{input}"])

    # Assert.
    assert version == "1.6.0"


def test_detect_parser_version_reads_pyproject_toml(tmp_path: Path) -> None:
    # Arrange.
    parser_root = tmp_path / "yini-parser-python"
    adapter_path = parser_root / "tools" / "yini_parser_adapter.py"
    adapter_path.parent.mkdir(parents=True)
    adapter_path.write_text("# adapter", encoding="utf-8")
    (parser_root / "pyproject.toml").write_text(
        '[project]\nname = "yini-parser"\nversion = "0.2.0b1"\n',
        encoding="utf-8",
    )

    # Act.
    version = detect_parser_version(["python", str(adapter_path), "--input", "{input}"])

    # Assert.
    assert version == "0.2.0b1"


def test_detect_parser_version_returns_not_detected_without_metadata(
    tmp_path: Path,
) -> None:
    # Arrange.
    parser_root = tmp_path / "yini-parser-custom"
    adapter_path = parser_root / "tools" / "adapter.py"
    adapter_path.parent.mkdir(parents=True)
    adapter_path.write_text("# adapter", encoding="utf-8")

    # Act.
    version = detect_parser_version(["python", str(adapter_path), "--input", "{input}"])

    # Assert.
    assert version == "not detected"


def test_format_summary_rule_falls_back_for_limited_terminal_encoding() -> None:
    # Act.
    summary_rule = format_summary_rule("cp1252")

    # Assert.
    assert summary_rule == "-" * 40


def test_get_yini_spec_revision_reads_packaged_case_manifest() -> None:
    # Act.
    revision = get_yini_spec_revision()

    # Assert.
    assert revision == "1.0.0-RC.6x"


@pytest.mark.parametrize(
    ("returncode", "stderr", "passed"),
    [
        pytest.param(1, "Invalid syntax.", True, id="rejected-input"),
        pytest.param(0, "", False, id="unexpected-success"),
        pytest.param(0, "Invalid syntax.", False, id="error-text-with-success-exit"),
    ],
)
def test_run_invalid_case_checks_exit_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    returncode: int,
    stderr: str,
    passed: bool,
) -> None:
    # Arrange.
    case = InvalidCase(yini_path=tmp_path / "invalid.yini")
    monkeypatch.setattr(
        "yini_test.runner.run_adapter_raw",
        lambda adapter_tokens, input_path, mode: AdapterResult(
            stdout="{}", stderr=stderr, returncode=returncode
        ),
    )

    # Act.
    result = run_invalid_case(case, adapter_tokens=[sys.executable], mode="strict")

    # Assert.
    assert result.case_path == case.yini_path
    assert result.passed is passed
    if not passed:
        assert "Invalid case was expected to fail, but succeeded" in result.message
        assert "stdout:\n{}" in result.message
        if stderr:
            assert f"stderr:\n{stderr}" in result.message


@pytest.fixture
def warning_case(tmp_path: Path) -> WarningCase:
    case = WarningCase(
        yini_path=tmp_path / "warning.yini",
        json_path=tmp_path / "warning.json",
        warning_path=tmp_path / "warning.warning.json",
    )
    case.json_path.write_text('{"name": "Demo"}', encoding="utf-8")
    case.warning_path.write_text(
        '[{"contains": "FIRST_WARNING"}, {"contains": "SECOND_WARNING"}]',
        encoding="utf-8",
    )
    return case


@pytest.mark.parametrize("case_kind", ["valid", "warning", "invalid"])
def test_adapter_timeout_fails_each_case_category(
    monkeypatch: pytest.MonkeyPatch,
    warning_case: WarningCase,
    case_kind: str,
) -> None:
    # Arrange.
    def time_out(
        command: list[str], *, timeout: float, **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(command, timeout)

    monkeypatch.setattr("yini_test.adapters.subprocess.run", time_out)
    adapter_tokens = [sys.executable, "--input", "{input}", "--mode", "{mode}"]

    # Act.
    if case_kind == "valid":
        result = run_valid_case(
            ValidCase(warning_case.yini_path, warning_case.json_path),
            adapter_tokens,
            mode="strict",
        )
    elif case_kind == "warning":
        result = run_warning_case(warning_case, adapter_tokens, mode="strict")
    else:
        result = run_invalid_case(
            InvalidCase(warning_case.yini_path), adapter_tokens, mode="strict"
        )

    # Assert.
    assert result.passed is False
    assert result.case_path == warning_case.yini_path
    assert (
        f"Adapter timed out for case: {warning_case.yini_path.name}" in result.message
    )
    assert f"--input {warning_case.yini_path} --mode strict" in result.message


@pytest.mark.parametrize(
    ("stdout", "stderr", "returncode", "error"),
    [
        pytest.param(
            '{"name": "Demo"}',
            "Extra diagnostic.\nSECOND_WARNING\nFIRST_WARNING",
            0,
            None,
            id="all-markers-in-stderr",
        ),
        pytest.param(
            '{"name": "Demo"}', "SECOND_WARNING", 0, "FIRST_WARNING", id="missing-first"
        ),
        pytest.param(
            '{"name": "Demo"}',
            "FIRST_WARNING",
            0,
            "SECOND_WARNING",
            id="missing-second",
        ),
        pytest.param(
            ' { "name": "Demo" } \n',
            "FIRST_WARNING\nSECOND_WARNING",
            2,
            "Adapter failed for warning case",
            id="nonzero-exit-with-correct-output",
        ),
        pytest.param(
            "", "FIRST_WARNING\nSECOND_WARNING", 0, "no JSON output", id="empty-stdout"
        ),
        pytest.param(
            '{"name":',
            "FIRST_WARNING\nSECOND_WARNING",
            0,
            "not valid JSON",
            id="malformed-json",
        ),
    ],
)
def test_run_warning_case_requires_success_json_and_all_warning_markers(
    monkeypatch: pytest.MonkeyPatch,
    warning_case: WarningCase,
    stdout: str,
    stderr: str,
    returncode: int,
    error: str | None,
) -> None:
    # Arrange.
    monkeypatch.setattr(
        "yini_test.runner.run_adapter_raw",
        lambda adapter_tokens, input_path, mode: AdapterResult(
            stdout=stdout, stderr=stderr, returncode=returncode
        ),
    )

    # Act.
    result = run_warning_case(warning_case, [sys.executable], mode="lenient")

    # Assert.
    assert result.case_path == warning_case.yini_path
    assert result.passed is (error is None)
    if error is not None:
        assert error in result.message


def test_run_warning_case_does_not_match_markers_in_stdout(
    monkeypatch: pytest.MonkeyPatch,
    warning_case: WarningCase,
) -> None:
    # Arrange.
    stdout = '{"name": "FIRST_WARNING SECOND_WARNING"}'
    warning_case.json_path.write_text(stdout, encoding="utf-8")
    monkeypatch.setattr(
        "yini_test.runner.run_adapter_raw",
        lambda adapter_tokens, input_path, mode: AdapterResult(
            stdout=stdout, stderr="", returncode=0
        ),
    )

    # Act.
    result = run_warning_case(warning_case, [sys.executable], mode="lenient")

    # Assert.
    assert result.passed is False
    assert "Warning mismatch for warning case" in result.message
    assert "FIRST_WARNING" in result.message


@pytest.mark.parametrize("failing_category", ["valid", "warning", "invalid"])
@pytest.mark.parametrize("fail_fast", [True, False], ids=["stop", "continue"])
def test_run_case_group_stops_only_when_fail_fast_is_enabled(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    failing_category: str,
    fail_fast: bool,
) -> None:
    # Arrange.
    case_paths: list[Path] = []
    for category in ("valid", "warning", "invalid"):
        category_dir = tmp_path / "smoke" / "lenient" / category
        category_dir.mkdir(parents=True)
        for name in ("1-first", "2-second"):
            yini_path = category_dir / f"{name}.yini"
            yini_path.write_text("name = 1", encoding="utf-8")
            if category != "invalid":
                yini_path.with_suffix(".json").write_text("{}", encoding="utf-8")
            if category == "warning":
                yini_path.with_suffix(".warning.json").write_text(
                    '[{"contains": "warning"}]', encoding="utf-8"
                )
            case_paths.append(yini_path)

    failing_path = tmp_path / "smoke" / "lenient" / failing_category / "1-first.yini"
    calls: list[Path] = []

    def fake_run_case(
        case: ValidCase | WarningCase | InvalidCase,
        adapter_tokens: list[str],
        mode: str,
        show_progress: bool = False,
    ) -> CaseResult:
        calls.append(case.yini_path)
        return CaseResult(
            case_path=case.yini_path, passed=case.yini_path != failing_path
        )

    monkeypatch.setattr("yini_test.runner.run_valid_case", fake_run_case)
    monkeypatch.setattr("yini_test.runner.run_warning_case", fake_run_case)
    monkeypatch.setattr("yini_test.runner.run_invalid_case", fake_run_case)

    # Act.
    results = run_case_group(
        "smoke", "lenient", tmp_path, [sys.executable], fail_fast=fail_fast
    )

    # Assert.
    expected_paths = case_paths
    if fail_fast:
        expected_paths = case_paths[: case_paths.index(failing_path) + 1]
    assert calls == expected_paths
    assert [result.case_path for result in results] == expected_paths
    assert sum(not result.passed for result in results) == 1


@pytest.mark.parametrize("fail_fast", [True, False], ids=["stop", "continue"])
def test_run_suite_matrix_fail_fast_counts_only_executed_cases(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    fail_fast: bool,
) -> None:
    # Arrange.
    calls: list[tuple[str, str]] = []
    fail_fast_values: list[bool] = []

    def fake_run_case_group(
        suite_name: str,
        mode: str,
        cases_root: Path,
        adapter_tokens: list[str],
        fail_fast: bool = False,
        show_progress: bool = False,
    ) -> list[CaseResult]:
        calls.append((suite_name, mode))
        fail_fast_values.append(fail_fast)
        results = [CaseResult(tmp_path / f"{suite_name}-{mode}-pass.yini", passed=True)]
        if (suite_name, mode) == ("smoke", "strict"):
            results.append(CaseResult(tmp_path / "failure.yini", passed=False))
        return results

    monkeypatch.setattr("yini_test.runner.run_case_group", fake_run_case_group)
    monkeypatch.setattr(
        "yini_test.runner.detect_parser_version", lambda adapter_tokens: "not detected"
    )

    # Act.
    exit_code = run_suite_matrix(
        "all", ["lenient", "strict"], tmp_path, [sys.executable], fail_fast=fail_fast
    )

    # Assert.
    output = capsys.readouterr().out
    assert exit_code == 1
    assert fail_fast_values == [fail_fast] * len(calls)
    assert "Result:  FAIL" in output
    assert "- smoke / strict: 1 failed" in output
    if fail_fast:
        assert calls == [("smoke", "lenient"), ("smoke", "strict")]
        assert "golden" not in output
        assert "Summary: 2 passed, 1 failed, 3 total" in output
    else:
        assert calls == [
            ("smoke", "lenient"),
            ("smoke", "strict"),
            ("golden", "lenient"),
            ("golden", "strict"),
        ]
        assert "Summary: 4 passed, 1 failed, 5 total" in output

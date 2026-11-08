from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest


@pytest.fixture
def cli_project(tmp_path: Path) -> tuple[Path, Path, Path]:
    project_dir = tmp_path / "project with spaces"
    cases_root = project_dir / "test cases"
    adapter_path = project_dir / "fake adapter.py"
    calls_path = project_dir / "adapter calls.jsonl"

    for suite in ("smoke", "golden"):
        for mode in ("lenient", "strict"):
            for category in ("valid", "warning", "invalid"):
                case_dir = cases_root / suite / mode / category
                case_dir.mkdir(parents=True)
                yini_path = case_dir / "sample.strict.yini"
                source = 'name = "Malm\u00f6"\n'
                yini_path.write_text(source, encoding="utf-8")
                if category != "invalid":
                    yini_path.with_suffix(".json").write_text(
                        json.dumps({"mode": mode, "source": source}), encoding="utf-8"
                    )
                if category == "warning":
                    yini_path.with_suffix(".warning.json").write_text(
                        '[{"contains": "TEST_WARNING"}]', encoding="utf-8"
                    )

    adapter_path.write_text(
        textwrap.dedent(
            """\
            import argparse
            import json
            from pathlib import Path
            import sys

            parser = argparse.ArgumentParser()
            parser.add_argument("--input", required=True)
            parser.add_argument("--mode", required=True)
            parser.add_argument("--calls-file", required=True)
            args = parser.parse_args()
            input_path = Path(args.input)
            with Path(args.calls_file).open("a", encoding="utf-8") as calls:
                calls.write(json.dumps({"path": args.input, "mode": args.mode}) + "\\n")

            if input_path.parent.name == "invalid":
                print("Invalid syntax.", file=sys.stderr)
                raise SystemExit(1)
            if input_path.parent.name == "warning":
                print("TEST_WARNING", file=sys.stderr)
            print(json.dumps(
                {"mode": args.mode, "source": input_path.read_text(encoding="utf-8")},
                ensure_ascii=False,
            ))
            """
        ),
        encoding="utf-8",
    )
    return cases_root, adapter_path, calls_path


def run_cli(
    project: tuple[Path, Path, Path], suite: str, options: list[str]
) -> subprocess.CompletedProcess[str]:
    cases_root, adapter_path, calls_path = project
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    environment["PYTHONIOENCODING"] = "utf-8"

    return subprocess.run(
        [
            sys.executable,
            "-m",
            "yini_test",
            suite,
            *options,
            "--cases-root",
            str(cases_root),
            "--adapter",
            sys.executable,
            str(adapter_path),
            "--input",
            "{input}",
            "--mode",
            "{mode}",
            "--calls-file",
            str(calls_path),
        ],
        cwd=adapter_path.parent,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )


@pytest.mark.parametrize(
    ("suite", "options", "expected_groups"),
    [
        pytest.param("smoke", [], [("smoke", "lenient")], id="default-lenient"),
        pytest.param("smoke", ["--strict"], [("smoke", "strict")], id="strict"),
        pytest.param(
            "all",
            ["--all-modes"],
            [
                ("smoke", "lenient"),
                ("smoke", "strict"),
                ("golden", "lenient"),
                ("golden", "strict"),
            ],
            id="all-suites-and-modes",
        ),
    ],
)
def test_cli_runs_adapter_with_spaced_paths_and_correct_modes(
    cli_project: tuple[Path, Path, Path],
    suite: str,
    options: list[str],
    expected_groups: list[tuple[str, str]],
) -> None:
    # Act.
    completed = run_cli(cli_project, suite, options)

    # Assert.
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stderr == ""
    total = len(expected_groups) * 3
    assert f"Summary: {total} passed, 0 failed, {total} total" in completed.stdout
    assert "Result:  PASS" in completed.stdout
    assert completed.stdout.count("PASS  ") == total
    cases_root, _, calls_path = cli_project
    calls = [
        json.loads(line) for line in calls_path.read_text(encoding="utf-8").splitlines()
    ]
    assert calls == [
        {
            "path": str(cases_root / suite / mode / category / "sample.strict.yini"),
            "mode": mode,
        }
        for suite, mode in expected_groups
        for category in ("valid", "warning", "invalid")
    ]


@pytest.mark.parametrize(
    ("suite", "options", "passed", "total"),
    [
        pytest.param("smoke", [], 2, 3, id="continue-after-failure"),
        pytest.param("all", ["--all-modes", "--fail-fast"], 0, 1, id="fail-fast"),
    ],
)
def test_cli_returns_failure_with_correct_execution_counts(
    cli_project: tuple[Path, Path, Path],
    suite: str,
    options: list[str],
    passed: int,
    total: int,
) -> None:
    # Arrange.
    cases_root, _, calls_path = cli_project
    expected_path = cases_root / "smoke" / "lenient" / "valid" / "sample.strict.json"
    expected_path.write_text("{}", encoding="utf-8")

    # Act.
    completed = run_cli(cli_project, suite, options)

    # Assert.
    assert completed.returncode == 1, completed.stdout + completed.stderr
    assert completed.stderr == ""
    assert "Output mismatch for valid case" in completed.stdout
    assert f"Summary: {passed} passed, 1 failed, {total} total" in completed.stdout
    assert "Result:  FAIL" in completed.stdout
    assert "- smoke / lenient: 1 failed" in completed.stdout
    assert len(calls_path.read_text(encoding="utf-8").splitlines()) == total
